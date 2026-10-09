"""F7 - JSON persistence.

- Missing file  -> fresh start (empty list).
- Malformed JSON or wrong shape -> StorageError with a clear message. The
  caller must NOT save over the file in that case, so data is never silently
  erased.
- Saving writes to a temporary file first and then swaps it in, so a crash
  mid-write cannot leave a half-written tickets file.
"""

import json
import os
import re

DEFAULT_PATH = os.path.join("data", "tickets.json")

REQUIRED_FIELDS = (
    "id",
    "title",
    "category",
    "urgency",
    "affected_users",
    "priority",
    "status",
    "assigned_to",
)

_ID_PATTERN = re.compile(r"^T\d+$")


class StorageError(ValueError):
    """The tickets file exists but cannot be trusted."""


def load_tickets(path=DEFAULT_PATH):
    """Return the saved list of tickets, or [] if the file does not exist."""
    if not os.path.exists(path):
        return []

    try:
        with open(path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
    except json.JSONDecodeError as error:
        raise StorageError(
            f"Tickets file '{path}' is not valid JSON ({error}). "
            "It was NOT changed. Fix it or move it aside to start fresh."
        ) from error
    except OSError as error:
        raise StorageError(f"Could not read '{path}': {error}") from error

    return _check_shape(data, path)


def _check_shape(data, path):
    if not isinstance(data, list):
        raise StorageError(
            f"Tickets file '{path}' must contain a list of tickets. "
            "It was NOT changed."
        )
    seen_ids = set()
    for index, ticket in enumerate(data, start=1):
        if not isinstance(ticket, dict):
            raise StorageError(f"Ticket #{index} in '{path}' is not an object.")
        missing = [name for name in REQUIRED_FIELDS if name not in ticket]
        if missing:
            raise StorageError(
                f"Ticket #{index} in '{path}' is missing: {', '.join(missing)}."
            )
        ticket_id = ticket["id"]
        if not isinstance(ticket_id, str) or not _ID_PATTERN.match(ticket_id):
            raise StorageError(f"Ticket #{index} has a malformed ID: {ticket_id!r}.")
        if ticket_id in seen_ids:
            raise StorageError(f"Duplicate ticket ID in '{path}': {ticket_id}.")
        seen_ids.add(ticket_id)
    return data


def save_tickets(tickets, path=DEFAULT_PATH):
    """Write tickets to path (creating the folder if needed)."""
    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)

    temp_path = path + ".tmp"
    with open(temp_path, "w", encoding="utf-8") as handle:
        json.dump(tickets, handle, indent=2)
    os.replace(temp_path, path)
