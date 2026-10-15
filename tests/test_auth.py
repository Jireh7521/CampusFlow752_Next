import json
import os
import tempfile
import unittest

from campusflow.auth import (
    AuthenticationError,
    authenticate,
    create_user,
    load_users,
    save_users,
    verify_password,
)


class TestAuthentication(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.path = os.path.join(self.folder.name, "users.json")

    def test_password_is_hashed_and_can_be_verified(self):
        users = []
        create_user(users, "Jireh", "A-long-test-password!")
        self.assertEqual(users[0]["username"], "jireh")
        self.assertNotIn("A-long-test-password!", users[0]["password_hash"])
        self.assertTrue(verify_password("A-long-test-password!", users[0]["password_hash"]))
        self.assertFalse(verify_password("wrong-password", users[0]["password_hash"]))

    def test_login_is_case_insensitive_and_rejects_bad_password(self):
        users = []
        create_user(users, "CampusUser", "A-long-test-password!")
        self.assertEqual(
            authenticate(users, "CAMPUSUSER", "A-long-test-password!"),
            "campususer",
        )
        with self.assertRaisesRegex(ValueError, "Invalid username or password"):
            authenticate(users, "campususer", "incorrect-password")

    def test_username_and_password_rules(self):
        with self.assertRaisesRegex(ValueError, "Username"):
            create_user([], "ab", "A-long-test-password!")
        with self.assertRaisesRegex(ValueError, "at least 12"):
            create_user([], "valid_user", "short")
        users = []
        create_user(users, "valid_user", "A-long-test-password!")
        with self.assertRaisesRegex(ValueError, "already exists"):
            create_user(users, "VALID_USER", "Another-long-password!")

    def test_save_and_load_accounts(self):
        users = []
        create_user(users, "samuel", "A-long-test-password!")
        save_users(users, self.path)
        loaded = load_users(self.path)
        self.assertEqual(authenticate(loaded, "samuel", "A-long-test-password!"), "samuel")

    def test_missing_file_starts_with_no_accounts(self):
        self.assertEqual(load_users(self.path), [])

    def test_malformed_account_file_is_rejected_without_overwrite(self):
        with open(self.path, "w", encoding="utf-8") as handle:
            handle.write("{not valid json")
        with self.assertRaises(AuthenticationError):
            load_users(self.path)
        with open(self.path, encoding="utf-8") as handle:
            self.assertEqual(handle.read(), "{not valid json")

    def test_invalid_utf8_account_file_is_rejected_without_overwrite(self):
        invalid_bytes = b"\xff\xfe"
        with open(self.path, "wb") as handle:
            handle.write(invalid_bytes)

        with self.assertRaises(AuthenticationError):
            load_users(self.path)

        with open(self.path, "rb") as handle:
            self.assertEqual(handle.read(), invalid_bytes)

    def test_invalid_hash_record_is_rejected(self):
        with open(self.path, "w", encoding="utf-8") as handle:
            json.dump([{"username": "valid_user", "password_hash": "plain-text"}], handle)
        with self.assertRaises(AuthenticationError):
            load_users(self.path)


if __name__ == "__main__":
    unittest.main()
