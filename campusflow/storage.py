"""F7 - JSON persistence.

- Missing file -> fresh start (empty list).
- Malformed JSON or invalid ticket data -> StorageError with a clear message.
  The caller must NOT save over the file in that case, so data is never silently
  erased.
- Saving writes to a temporary file first and then swaps it in, so a crash
  mid-write cannot leave a half-written tickets file.
"""

import copy
import json
import os
import re

from campusflow.tickets import (
    CATEGORIES,
    URGENCIES,
    calculate_priority,
    normalize_category,
    normalize_urgency,
    validate_affected_users,
    validate_title,
)
from campusflow.workflow import VALID_STATUSES

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
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise StorageError(
            f"Tickets file '{path}' is not valid JSON ({error}). "
            "It was NOT changed. Fix it or move it aside to start fresh."
        ) from error
    except OSError as error:
        raise StorageError(f"Could not read '{path}': {error}") from error

    return _check_shape(data, path)


def _check_shape(data, path):
    """Validate the entire collection before returning it to the application."""
    if not isinstance(data, list):
        raise StorageError(
            f"Tickets file '{path}' must contain a list of tickets. "
            "It was NOT changed."
        )

    # Legacy-note migration mutates records, so validate a deep copy. If any
    # later record is invalid, the caller's original collection stays intact.
    validated_data = copy.deepcopy(data)
    seen_ids = set()
    for index, ticket in enumerate(validated_data, start=1):
        if not isinstance(ticket, dict):
            raise StorageError(f"Ticket #{index} in '{path}' is not an object.")

        missing = [name for name in REQUIRED_FIELDS if name not in ticket]
        if missing:
            raise StorageError(
                f"Ticket #{index} in '{path}' is missing: {', '.join(missing)}."
            )

        ticket_id = ticket["id"]
        if not isinstance(ticket_id, str) or not _ID_PATTERN.fullmatch(ticket_id):
            raise StorageError(f"Ticket #{index} has a malformed ID: {ticket_id!r}.")
        if ticket_id in seen_ids:
            raise StorageError(f"Duplicate ticket ID in '{path}': {ticket_id}.")
        seen_ids.add(ticket_id)

        try:
            title = validate_title(ticket["title"])
            category = normalize_category(ticket["category"])
            urgency = normalize_urgency(ticket["urgency"])
            affected_users = validate_affected_users(ticket["affected_users"])
        except (TypeError, ValueError) as error:
            raise StorageError(
                f"Ticket {ticket_id} contains invalid core fields: {error}"
            ) from error

        # Persisted records must use canonical values and a priority that agrees
        # with the project's priority rules; don't silently repair bad records.
        if title != ticket["title"]:
            raise StorageError(f"Ticket {ticket_id} title must be trimmed.")
        if category != ticket["category"] or category not in CATEGORIES:
            raise StorageError(f"Ticket {ticket_id} has a non-canonical category.")
        if urgency != ticket["urgency"] or urgency not in URGENCIES:
            raise StorageError(f"Ticket {ticket_id} has a non-canonical urgency.")

        expected_priority = calculate_priority(urgency, affected_users)
        if ticket["priority"] != expected_priority:
            raise StorageError(
                f"Ticket {ticket_id} priority '{ticket['priority']}' does not match "
                f"the calculated priority '{expected_priority}'."
            )

        if ticket["status"] not in VALID_STATUSES:
            raise StorageError(
                f"Ticket {ticket_id} has an invalid status: {ticket['status']!r}."
            )

        assignee = ticket["assigned_to"]
        if assignee is not None and (
            not isinstance(assignee, str) or not assignee.strip()
        ):
            raise StorageError(f"Ticket {ticket_id} has an invalid assignee.")

        # Older saved tickets predate follow-up notes; migrate them in memory.
        ticket.setdefault("notes", [])
        notes = ticket["notes"]
        if not isinstance(notes, list):
            raise StorageError(f"Ticket {ticket_id} notes must be a list.")

        seen_note_ids = set()
        for note in notes:
            if not isinstance(note, dict) or not all(
                key in note for key in ("note_id", "author", "message")
            ):
                raise StorageError(
                    f"Ticket {ticket_id} contains a malformed follow-up note."
                )

            note_id = note["note_id"]
            author = note["author"]
            message = note["message"]
            if (
                not isinstance(note_id, str)
                or not re.fullmatch(r"N\d+", note_id)
                or note_id in seen_note_ids
                or not isinstance(author, str)
                or not author.strip()
                or not isinstance(message, str)
                or not 5 <= len(message.strip()) <= 300
            ):
                raise StorageError(
                    f"Ticket {ticket_id} contains an invalid follow-up note."
                )
            seen_note_ids.add(note_id)

    return validated_data


def save_tickets(tickets, path=DEFAULT_PATH):
    """Write tickets to path (creating the folder if needed)."""
    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)

    temp_path = path + ".tmp"
    try:
        with open(temp_path, "w", encoding="utf-8") as handle:
            json.dump(tickets, handle, indent=2)
        os.replace(temp_path, path)
    except BaseException:
        # A failed write or replace must not leave a stale temporary file.
        # Preserve the original exception if cleanup itself is unsuccessful.
        try:
            os.remove(temp_path)
        except OSError:
            pass
        raise
