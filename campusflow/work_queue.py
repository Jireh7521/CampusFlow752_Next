"""F5 - Work queue: open tickets ordered by priority, then by ticket number.

Named work_queue (not queue) to avoid any confusion with Python's stdlib
`queue` module.
"""

PRIORITY_RANK = {"critical": 0, "high": 1, "medium": 2, "low": 3}


def ticket_number(ticket):
    """Numeric part of a ticket ID: 'T010' -> 10.

    Sorting on the number (not the string) keeps the order right even if IDs
    outgrow their zero-padding (T999, T1000).
    """
    ticket_id = str(ticket.get("id", ""))
    digits = ticket_id[1:]
    if not digits.isdigit():
        raise ValueError(f"Malformed ticket ID: '{ticket_id}'")
    return int(digits)


def get_work_queue(tickets):
    """Return a NEW list of open tickets: critical -> high -> medium -> low.

    Ties on priority are broken by the earlier (smaller) numeric ticket ID.
    Only tickets with status 'open' are queued; in_progress and resolved
    tickets are excluded. The input list is not modified.
    Raises ValueError if a queued ticket has an unknown priority or bad ID.
    """
    queue = [t for t in tickets if t.get("status") == "open"]

    def sort_key(ticket):
        priority = ticket.get("priority")
        if priority not in PRIORITY_RANK:
            raise ValueError(
                f"Ticket {ticket.get('id')} has unknown priority '{priority}'."
            )
        return (PRIORITY_RANK[priority], ticket_number(ticket))

    return sorted(queue, key=sort_key)
