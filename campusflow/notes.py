"""Structured follow-up notes for CampusFlow tickets."""

import re

from campusflow.workflow import find_ticket

_NOTE_ID_PATTERN = re.compile(r"N(\d+)")


def _next_note_id(notes):
    """Generate the next per-ticket note ID from saved notes."""
    highest = 0
    for note in notes:
        match = _NOTE_ID_PATTERN.fullmatch(str(note.get("note_id", "")))
        if match:
            highest = max(highest, int(match.group(1)))
    return f"N{highest + 1:03d}"


def _validate_existing_notes(notes):
    """Reject malformed in-memory notes before an append can partially mutate a ticket."""
    seen_ids = set()
    for note in notes:
        if not isinstance(note, dict):
            raise ValueError("Existing ticket notes must be valid note records.")

        note_id = note.get("note_id")
        match = _NOTE_ID_PATTERN.fullmatch(note_id) if isinstance(note_id, str) else None
        if match is None:
            raise ValueError("Existing ticket notes must have valid note IDs.")

        numeric_id = int(match.group(1))
        if numeric_id in seen_ids:
            raise ValueError("Existing ticket notes must have unique note IDs.")
        seen_ids.add(numeric_id)

        author = note.get("author")
        message = note.get("message")
        if not isinstance(author, str) or not author.strip():
            raise ValueError("Existing ticket notes must have a nonblank author.")
        if not isinstance(message, str) or not 5 <= len(message.strip()) <= 300:
            raise ValueError("Existing ticket notes must have a message between 5 and 300 characters.")


def add_note(tickets, ticket_id, author, message):
    """Validate and append a note only when its ticket is modifiable."""
    ticket = find_ticket(tickets, ticket_id)
    if ticket.get("status") not in ("open", "in_progress"):
        raise ValueError(
            f"Ticket {ticket['id']} does not accept notes while "
            f"its status is '{ticket.get('status')}'. Reopen it first."
        )
    if not isinstance(author, str) or not author.strip():
        raise ValueError("Note author must not be blank.")
    if not isinstance(message, str):
        raise ValueError("Note message must be between 5 and 300 characters.")
    message = message.strip()
    if not 5 <= len(message) <= 300:
        raise ValueError("Note message must be between 5 and 300 characters.")

    existing = ticket.get("notes", [])
    if not isinstance(existing, list):
        raise ValueError("Ticket notes must be a list.")
    _validate_existing_notes(existing)
    note = {
        "note_id": _next_note_id(existing),
        "author": author.strip(),
        "message": message,
    }
    ticket.setdefault("notes", []).append(note)
    ticket["notes"].sort(key=lambda item: int(item["note_id"][1:]))
    return ticket
