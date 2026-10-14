"""F1 (create + validation + priority), F2 (list/view) and F3 (assign).

Contract (see docs/design-decisions.md):
- Tickets are a list of dicts passed in as an argument.
- Invalid input raises ValueError with a clear message; nothing is changed.
- Functions return the ticket (or a string for display helpers); the CLI prints.
"""

import re

from campusflow.workflow import ensure_modifiable, find_ticket

CATEGORIES = ("Network", "Hardware", "Software", "Other")
URGENCIES = ("low", "medium", "high")

_ID_PATTERN = re.compile(r"^T(\d+)$")


# ---------- validation / normalization ----------

def validate_title(title):
    """Return the stripped title; reject blank or non-text titles."""
    if not isinstance(title, str) or not title.strip():
        raise ValueError("Title must not be blank.")
    return title.strip()


def normalize_category(category):
    """Accept any case ('network', 'NETWORK') and return the canonical name."""
    if isinstance(category, str):
        for allowed in CATEGORIES:
            if category.strip().lower() == allowed.lower():
                return allowed
    raise ValueError(
        f"Invalid category '{category}'. Choose one of: {', '.join(CATEGORIES)}."
    )


def normalize_urgency(urgency):
    """Accept any case ('HIGH', ' High ') and return the lowercase name."""
    if isinstance(urgency, str):
        value = urgency.strip().lower()
        if value in URGENCIES:
            return value
    raise ValueError(
        f"Invalid urgency '{urgency}'. Choose one of: {', '.join(URGENCIES)}."
    )


def validate_affected_users(value):
    """Return a positive int; reject booleans, floats, strings and non-positive values."""
    message = "Affected users must be a positive whole number (1 or more)."
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError(message)
    return value


def parse_affected_users_input(value):
    """Convert raw CLI text to an integer, then apply the shared validation."""
    message = "Affected users must be a positive whole number (1 or more)."
    if not isinstance(value, str):
        raise ValueError(message)
    try:
        number = int(value.strip())
    except ValueError:
        raise ValueError(message) from None
    return validate_affected_users(number)


def validate_staff_name(staff_name):
    """Return a stripped staff name, rejecting blank or non-text values."""
    if not isinstance(staff_name, str) or not staff_name.strip():
        raise ValueError("Staff member name must not be blank.")
    return staff_name.strip()


# ---------- priority engine ----------

def calculate_priority(urgency, affected_users):
    """Apply the four rules in order; the first match wins.

    1. high AND >= 10 users   -> critical
    2. high OR  >= 10 users   -> high
    3. medium OR >= 3 users   -> medium
    4. everything else        -> low
    """
    urgency = normalize_urgency(urgency)
    users = validate_affected_users(affected_users)

    if urgency == "high" and users >= 10:
        return "critical"
    if urgency == "high" or users >= 10:
        return "high"
    if urgency == "medium" or users >= 3:
        return "medium"
    return "low"


# ---------- F1: create ----------

def next_ticket_id(tickets):
    """Next unique ID: one more than the largest existing number (T001, T002...).

    Based on the max (not the count) so IDs stay unique after a reload.
    """
    highest = 0
    for ticket in tickets:
        match = _ID_PATTERN.match(str(ticket.get("id", "")))
        if match:
            highest = max(highest, int(match.group(1)))
    return f"T{highest + 1:03d}"


def create_ticket(tickets, title, category, urgency, affected_users):
    """Validate everything first, then append and return the new ticket."""
    title = validate_title(title)
    category = normalize_category(category)
    urgency = normalize_urgency(urgency)
    users = validate_affected_users(affected_users)

    ticket = {
        "id": next_ticket_id(tickets),
        "title": title,
        "category": category,
        "urgency": urgency,
        "affected_users": users,
        "priority": calculate_priority(urgency, users),
        "status": "open",
        "assigned_to": None,
    }
    tickets.append(ticket)
    return ticket


# ---------- F3: assign ----------

def assign_ticket(tickets, ticket_id, staff_name):
    """Assign a ticket to a non-empty staff name.

    Rejects unknown IDs, blank names, and resolved tickets (they must be
    reopened first).
    """
    ticket = find_ticket(tickets, ticket_id)
    staff_name = validate_staff_name(staff_name)
    ensure_modifiable(ticket)
    ticket["assigned_to"] = staff_name
    return ticket


# ---------- F2: list / view ----------

def format_ticket(ticket):
    """Full details of one ticket as text."""
    assignee = ticket.get("assigned_to") or "(unassigned)"
    return "\n".join(
        [
            f"ID:             {ticket['id']}",
            f"Title:          {ticket['title']}",
            f"Category:       {ticket['category']}",
            f"Urgency:        {ticket['urgency']}",
            f"Affected users: {ticket['affected_users']}",
            f"Priority:       {ticket['priority']}",
            f"Status:         {ticket['status']}",
            f"Assigned to:    {assignee}",
        ]
    )


def format_ticket_list(tickets):
    """One line per ticket, in creation order; friendly message when empty."""
    if not tickets:
        return "No tickets yet."
    lines = []
    for t in tickets:
        assignee = t.get("assigned_to") or "unassigned"
        lines.append(
            f"{t['id']} | {t['priority']:<8} | {t['status']:<11} | "
            f"{t['title']} | {assignee}"
        )
    return "\n".join(lines)


# ---------- F4: search tickets ----------

SEARCH_CATEGORIES = CATEGORIES
SEARCH_STATUSES = ("open", "in_progress", "resolved")
SEARCH_PRIORITIES = ("critical", "high", "medium", "low")


def _normalize_search_filter(value, allowed, label):
    """Normalize an optional exact-match filter, accepting any letter case."""
    if value is None or (isinstance(value, str) and not value.strip()):
        return None
    if isinstance(value, str):
        candidate = value.strip().casefold()
        for option in allowed:
            if candidate == option.casefold():
                return option
    choices = ", ".join(allowed)
    raise ValueError(f"Invalid {label} filter '{value}'. Choose one of: {choices}.")


def search_tickets(tickets, title_query="", category=None, status=None, priority=None):
    """Search title substrings and apply optional category/status/priority filters.

    Matching is case-insensitive (Unicode-aware via casefold). All supplied
    filters are combined with AND semantics. Empty filters impose no restriction.
    This function only reads ticket data and never mutates it.
    """
    if title_query is None:
        title_query = ""
    if not isinstance(title_query, str):
        raise ValueError("Title search must be text.")

    category = _normalize_search_filter(category, SEARCH_CATEGORIES, "category")
    status = _normalize_search_filter(status, SEARCH_STATUSES, "status")
    priority = _normalize_search_filter(priority, SEARCH_PRIORITIES, "priority")
    needle = title_query.strip().casefold()

    return [
        ticket
        for ticket in tickets
        if (not needle or needle in str(ticket.get("title", "")).casefold())
        and (category is None or str(ticket.get("category", "")).casefold() == category.casefold())
        and (status is None or str(ticket.get("status", "")).casefold() == status.casefold())
        and (priority is None or str(ticket.get("priority", "")).casefold() == priority.casefold())
    ]


def sort_tickets_by_priority(tickets):
    """Return a new list ordered critical, high, medium, low, then numeric ID."""
    priority_rank = {priority: index for index, priority in enumerate(SEARCH_PRIORITIES)}

    def sort_key(ticket):
        priority = str(ticket.get("priority", "")).casefold()
        ticket_id = str(ticket.get("id", ""))
        match = _ID_PATTERN.match(ticket_id)
        numeric_id = int(match.group(1)) if match else float("inf")
        return (priority_rank.get(priority, len(priority_rank)), numeric_id, ticket_id)

    return sorted(tickets, key=sort_key)


def format_search_results(tickets):
    """Format the requested read-only search result columns."""
    if not tickets:
        return "No matching tickets found."
    headers = ("ID", "Title", "Category", "Priority", "Status", "Assignee")
    rows = [
        (
            str(ticket.get("id", "")),
            str(ticket.get("title", "")),
            str(ticket.get("category", "")),
            str(ticket.get("priority", "")),
            str(ticket.get("status", "")),
            str(ticket.get("assigned_to") or "unassigned"),
        )
        for ticket in tickets
    ]
    widths = [max(len(headers[i]), *(len(row[i]) for row in rows)) for i in range(len(headers))]
    lines = [" | ".join(headers[i].ljust(widths[i]) for i in range(len(headers)))]
    lines.append("-+-".join("-" * width for width in widths))
    lines.extend(" | ".join(row[i].ljust(widths[i]) for i in range(len(headers))) for row in rows)
    return "\n".join(lines)
