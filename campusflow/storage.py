"""F7 - safe JSON persistence and complete collection validation.

- Missing file -> a fresh start (empty list).
- Invalid JSON or any invalid ticket/note rejects the entire collection.
- Legacy tickets without notes are migrated only after every record validates.
- Saving uses a temporary file and atomic replacement.
"""

import copy
import json
import os
import re

from campusflow.tickets import CATEGORIES, URGENCIES, calculate_priority
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

_TICKET_ID_PATTERN = re.compile(r"^T(\d+)$")
_NOTE_ID_PATTERN = re.compile(r"^N(\d+)$")


class StorageError(ValueError):
    """The tickets file exists but cannot be trusted."""


def load_tickets(path=DEFAULT_PATH):
    """Return a validated ticket list, or [] if the file does not exist."""
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
    """Validate the whole collection before returning a migrated copy."""
    if not isinstance(data, list):
        raise StorageError(
            f"Tickets file '{path}' must contain a list of tickets. It was NOT changed."
        )

    # Work on a copy: neither validation nor legacy migration mutates caller state.
    tickets = copy.deepcopy(data)
    seen_ticket_ids = set()

    for index, ticket in enumerate(tickets, start=1):
        if not isinstance(ticket, dict):
            raise StorageError(f"Ticket #{index} in '{path}' is not an object.")

        missing = [name for name in REQUIRED_FIELDS if name not in ticket]
        if missing:
            raise StorageError(
                f"Ticket #{index} in '{path}' is missing: {', '.join(missing)}."
            )

        ticket_id = ticket["id"]
        match = _TICKET_ID_PATTERN.fullmatch(ticket_id) if isinstance(ticket_id, str) else None
        if match is None:
            raise StorageError(f"Ticket #{index} has a malformed ID: {ticket_id!r}.")

        # Compare numeric identity too, so T1 and T001 cannot refer to the same ticket.
        numeric_ticket_id = int(match.group(1))
        if numeric_ticket_id in seen_ticket_ids:
            raise StorageError(f"Duplicate ticket ID in '{path}': {ticket_id}.")
        seen_ticket_ids.add(numeric_ticket_id)

        title = ticket["title"]
        if not isinstance(title, str) or not title.strip():
            raise StorageError(f"Ticket {ticket_id} must have a nonblank title.")

        category = ticket["category"]
        if category not in CATEGORIES:
            raise StorageError(
                f"Ticket {ticket_id} has an invalid category: {category!r}."
            )

        urgency = ticket["urgency"]
        if urgency not in URGENCIES:
            raise StorageError(
                f"Ticket {ticket_id} has an invalid urgency: {urgency!r}."
            )

        users = ticket["affected_users"]
        if isinstance(users, bool) or not isinstance(users, int) or users < 1:
            raise StorageError(
                f"Ticket {ticket_id} affected_users must be a positive whole number."
            )

        expected_priority = calculate_priority(urgency, users)
        if ticket["priority"] != expected_priority:
            raise StorageError(
                f"Ticket {ticket_id} priority is inconsistent: expected "
                f"{expected_priority!r} for its urgency and affected_users."
            )

        if ticket["status"] not in VALID_STATUSES:
            raise StorageError(
                f"Ticket {ticket_id} has an invalid status: {ticket['status']!r}."
            )

        assignee = ticket["assigned_to"]
        if assignee is not None and (
            not isinstance(assignee, str) or not assignee.strip()
        ):
            raise StorageError(
                f"Ticket {ticket_id} assigned_to must be null or a nonblank name."
            )

        notes = ticket.get("notes", [])
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
            note_match = (
                _NOTE_ID_PATTERN.fullmatch(note_id)
                if isinstance(note_id, str)
                else None
            )
            author = note["author"]
            message = note["message"]
            if (
                note_match is None
                or int(note_match.group(1)) in seen_note_ids
                or not isinstance(author, str)
                or not author.strip()
                or not isinstance(message, str)
                or not 5 <= len(message.strip()) <= 300
            ):
                raise StorageError(
                    f"Ticket {ticket_id} contains an invalid or duplicate follow-up note."
                )
            seen_note_ids.add(int(note_match.group(1)))

    # Migrate legacy records only after every ticket and note has validated.
    for ticket in tickets:
        ticket.setdefault("notes", [])

    return tickets


def save_tickets(tickets, path=DEFAULT_PATH):
    """Validate and write tickets to path (creating the folder if needed)."""
    validated_tickets = _check_shape(tickets, path)
    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)

    temp_path = path + ".tmp"
    try:
        with open(temp_path, "w", encoding="utf-8") as handle:
            json.dump(validated_tickets, handle, indent=2)
        os.replace(temp_path, path)
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
