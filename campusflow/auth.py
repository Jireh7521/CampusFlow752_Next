"""Local username/password authentication for the CampusFlow CLI.

Passwords are stored as salted scrypt hashes, never as plain text.
This protects the application login; it is not an operating-system security boundary.
"""

import hashlib
import hmac
import json
import os
import re
import secrets

DEFAULT_USERS_PATH = os.path.join("data", "users.json")
_SCRYPT_N = 2**14
_SCRYPT_R = 8
_SCRYPT_P = 1
_SALT_BYTES = 16
_KEY_BYTES = 64
_USERNAME_PATTERN = re.compile(r"^[a-zA-Z0-9_.-]{3,32}$")


class AuthenticationError(ValueError):
    """Stored account data is unreadable or unsafe."""


def load_users(path=DEFAULT_USERS_PATH):
    """Load accounts, returning an empty list when the account file is absent."""
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as handle:
            users = json.load(handle)
    except (OSError, json.JSONDecodeError) as error:
        raise AuthenticationError(
            f"Could not safely read accounts from '{path}'. The file was not changed."
        ) from error

    if not isinstance(users, list):
        raise AuthenticationError(f"Accounts file '{path}' must contain a list.")

    seen = set()
    for account in users:
        if not isinstance(account, dict):
            raise AuthenticationError("Accounts file contains an invalid account.")
        username = account.get("username")
        password_hash = account.get("password_hash")
        if (
            not isinstance(username, str)
            or not _USERNAME_PATTERN.fullmatch(username)
            or not isinstance(password_hash, str)
            or not _is_supported_hash(password_hash)
        ):
            raise AuthenticationError("Accounts file contains invalid account data.")
        normalized = username.casefold()
        if normalized in seen:
            raise AuthenticationError("Accounts file contains duplicate usernames.")
        seen.add(normalized)
    return users


def _is_supported_hash(value):
    parts = value.split("$")
    if len(parts) != 6 or parts[0] != "scrypt":
        return False
    try:
        n, r, p = (int(parts[1]), int(parts[2]), int(parts[3]))
        salt = bytes.fromhex(parts[4])
        digest = bytes.fromhex(parts[5])
    except (ValueError, TypeError):
        return False
    return (
        n == _SCRYPT_N
        and r == _SCRYPT_R
        and p == _SCRYPT_P
        and len(salt) == _SALT_BYTES
        and len(digest) == _KEY_BYTES
    )


def _hash_password(password):
    salt = secrets.token_bytes(_SALT_BYTES)
    digest = hashlib.scrypt(
        password.encode("utf-8"),
        salt=salt,
        n=_SCRYPT_N,
        r=_SCRYPT_R,
        p=_SCRYPT_P,
        dklen=_KEY_BYTES,
    )
    return f"scrypt\u0024{_SCRYPT_N}\u0024{_SCRYPT_R}\u0024{_SCRYPT_P}\u0024{salt.hex()}\u0024{digest.hex()}"


def verify_password(password, password_hash):
    """Return whether password matches a supported stored hash."""
    if not isinstance(password, str) or not isinstance(password_hash, str):
        return False
    if not _is_supported_hash(password_hash):
        return False
    _, n, r, p, salt_hex, expected_hex = password_hash.split("$")
    actual = hashlib.scrypt(
        password.encode("utf-8"),
        salt=bytes.fromhex(salt_hex),
        n=int(n),
        r=int(r),
        p=int(p),
        dklen=_KEY_BYTES,
    )
    return hmac.compare_digest(actual, bytes.fromhex(expected_hex))


def create_user(users, username, password):
    """Validate and append a new account. Returns its normalized username."""
    if not isinstance(username, str) or not _USERNAME_PATTERN.fullmatch(username.strip()):
        raise ValueError(
            "Username must be 3-32 characters and use only letters, numbers, '.', '_' or '-'."
        )
    normalized = username.strip().casefold()
    if any(account["username"].casefold() == normalized for account in users):
        raise ValueError("That username already exists.")
    if not isinstance(password, str) or len(password) < 12:
        raise ValueError("Password must be at least 12 characters long.")
    if len(password) > 1024:
        raise ValueError("Password is too long.")

    users.append({"username": normalized, "password_hash": _hash_password(password)})
    return normalized


def authenticate(users, username, password):
    """Return the account username on success, otherwise raise a generic error."""
    normalized = username.strip().casefold() if isinstance(username, str) else ""
    for account in users:
        if account["username"].casefold() == normalized:
            if verify_password(password, account["password_hash"]):
                return account["username"]
            break
    raise ValueError("Invalid username or password.")


def save_users(users, path=DEFAULT_USERS_PATH):
    """Save accounts atomically and restrict the file to its owner where supported."""
    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    temp_path = path + ".tmp"
    try:
        with open(temp_path, "w", encoding="utf-8") as handle:
            json.dump(users, handle, indent=2)
            handle.write("\n")
        try:
            os.chmod(temp_path, 0o600)
        except OSError:
            # Some platforms do not support POSIX permission bits.
            pass
        os.replace(temp_path, path)
        try:
            os.chmod(path, 0o600)
        except OSError:
            pass
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
