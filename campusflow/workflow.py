"""F4 - Ticket workflow: status transitions and reopen rules.

Contract (see docs/design-decisions.md):
- Tickets are a list of dicts; functions take that list as an argument.
- Invalid input or an illegal move raises ValueError with a clear message.
- All checks happen BEFORE the ticket is changed, so a rejected call never
  leaves a half-modified ticket.
- On success the updated ticket dict is returned; the CLI does the printing.
"""

import re

STATUS_OPEN = "open"
STATUS_IN_PROGRESS = "in_progress"
STATUS_RESOLVED = "resolved"

VALID_STATUSES = (STATUS_OPEN, STATUS_IN_PROGRESS, STATUS_RESOLVED)
_TICKET_ID_PATTERN = re.compile(r"T\d+")

# status -> set of statuses it may move to.
# resolved may only go back to open (an explicit reopen).
ALLOWED_TRANSITIONS = {
    STATUS_OPEN: {STATUS_IN_PROGRESS},
    STATUS_IN_PROGRESS: {STATUS_RESOLVED},
    STATUS_RESOLVED: {STATUS_OPEN},
}


def validate_ticket_id(ticket_id):
    """Return a normalized ticket ID, rejecting malformed input consistently."""
    if not isinstance(ticket_id, str):
        raise ValueError("Ticket ID must be text in the format T001.")
    wanted = ticket_id.strip().upper()
    if not wanted:
        raise ValueError("Ticket ID must not be blank.")
    if _TICKET_ID_PATTERN.fullmatch(wanted) is None:
        raise ValueError("Ticket ID must use the format T001 (T followed by digits).")
    return wanted


def find_ticket(tickets, ticket_id):
    """Return the ticket with this ID (case/whitespace tolerant).

    Raises ValueError for malformed IDs and valid-but-unknown IDs.
    """
    wanted = validate_ticket_id(ticket_id)
    for ticket in tickets:
        if ticket.get("id") == wanted:
            return ticket
    raise ValueError(f"Unknown ticket ID: {wanted}")


def ensure_modifiable(ticket):
    """Raise ValueError if the ticket is resolved.

    A resolved ticket may only be modified after an explicit reopen. Other
    modules (e.g. assignment) should call this before changing a ticket.
    """
    if ticket.get("status") == STATUS_RESOLVED:
        raise ValueError(
            f"Ticket {ticket.get('id')} is resolved and cannot be modified. "
            "Reopen it first."
        )


def _has_assignee(ticket):
    assignee = ticket.get("assigned_to")
    return isinstance(assignee, str) and assignee.strip() != ""


def change_status(tickets, ticket_id, new_status):
    """Move a ticket to new_status if the transition is allowed.

    Check order: ticket exists -> new status is valid -> transition is in the
    table -> unassigned ticket cannot enter in_progress.

    Returns the updated ticket. Raises ValueError (ticket unchanged) otherwise.
    """
    ticket = find_ticket(tickets, ticket_id)

    if not isinstance(new_status, str):
        raise ValueError(
            f"Invalid status '{new_status}'. "
            f"Choose one of: {', '.join(VALID_STATUSES)}."
        )
    target = new_status.strip().lower()
    if target not in VALID_STATUSES:
        raise ValueError(
            f"Invalid status '{new_status}'. "
            f"Choose one of: {', '.join(VALID_STATUSES)}."
        )

    current = ticket.get("status")
    if target not in ALLOWED_TRANSITIONS.get(current, set()):
        if current == STATUS_RESOLVED:
            raise ValueError(
                f"Ticket {ticket['id']} is resolved. "
                "It can only be reopened (resolved -> open)."
            )
        raise ValueError(
            f"Invalid transition for {ticket['id']}: {current} -> {target}."
        )

    if target == STATUS_IN_PROGRESS and not _has_assignee(ticket):
        raise ValueError(
            f"Ticket {ticket['id']} is unassigned. "
            "Assign it before moving it to in_progress."
        )

    ticket["status"] = target
    return ticket


def reopen_ticket(tickets, ticket_id):
    """Explicitly reopen a resolved ticket (resolved -> open).

    Raises ValueError if the ticket is unknown or is not resolved.
    """
    ticket = find_ticket(tickets, ticket_id)
    if ticket.get("status") != STATUS_RESOLVED:
        raise ValueError(
            f"Ticket {ticket['id']} is not resolved, so it cannot be reopened."
        )
    ticket["status"] = STATUS_OPEN
    return ticket
