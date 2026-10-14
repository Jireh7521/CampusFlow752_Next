"""F6 - Reports: ticket totals, breakdowns, and resolution metrics."""

from campusflow.tickets import CATEGORIES

STATUSES = ("open", "in_progress", "resolved")
PRIORITIES = ("critical", "high", "medium", "low")


def build_report(tickets):
    """Build report metrics from the tickets' current state.

    Every known status, priority, and category is present, including zero
    counts. A ticket is counted once in each breakdown. Invalid values raise
    ValueError instead of silently making the report inaccurate.
    """
    ticket_list = list(tickets)
    by_status = {status: 0 for status in STATUSES}
    by_priority = {priority: 0 for priority in PRIORITIES}
    by_category = {category: 0 for category in CATEGORIES}

    for ticket in ticket_list:
        status = ticket.get("status")
        priority = ticket.get("priority")
        category = ticket.get("category")

        if status not in by_status:
            raise ValueError(
                f"Ticket {ticket.get('id')} has unknown status '{status}'."
            )
        if priority not in by_priority:
            raise ValueError(
                f"Ticket {ticket.get('id')} has unknown priority '{priority}'."
            )
        if category not in by_category:
            raise ValueError(
                f"Ticket {ticket.get('id')} has unknown category '{category}'."
            )

        by_status[status] += 1
        by_priority[priority] += 1
        by_category[category] += 1

    total = len(ticket_list)
    resolved = by_status["resolved"]
    unresolved = by_status["open"] + by_status["in_progress"]
    resolution_percentage = (resolved / total * 100) if total else 0

    return {
        "total": total,
        "by_status": by_status,
        "by_priority": by_priority,
        "by_category": by_category,
        "unresolved": unresolved,
        "resolved": resolved,
        "resolution_percentage": resolution_percentage,
    }


def format_report(report):
    """Turn a report dictionary into printable text for the CLI."""
    lines = [f"Total tickets: {report['total']}", "", "By status:"]
    for status, count in report["by_status"].items():
        lines.append(f"  {status}: {count}")

    lines.extend(["", "By priority:"])
    for priority, count in report["by_priority"].items():
        lines.append(f"  {priority}: {count}")

    lines.extend(["", "By category:"])
    for category, count in report["by_category"].items():
        lines.append(f"  {category}: {count}")

    percentage = f"{report['resolution_percentage']:.2f}".rstrip("0").rstrip(".")
    lines.extend(
        [
            "",
            f"Unresolved tickets: {report['unresolved']}",
            f"Resolved tickets: {report['resolved']}",
            f"Resolution percentage: {percentage}%",
        ]
    )
    return "\n".join(lines)
