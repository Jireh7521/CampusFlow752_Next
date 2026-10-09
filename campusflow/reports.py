"""F6 - Reports: totals plus breakdowns by status and by priority."""

STATUSES = ("open", "in_progress", "resolved")
PRIORITIES = ("critical", "high", "medium", "low")


def build_report(tickets):
    """Return {"total": n, "by_status": {...}, "by_priority": {...}}.

    Every known status and priority is always present (count 0 if unused), so
    an empty ticket list produces a valid report instead of a crash or blank.
    Raises ValueError if a ticket has an unknown status or priority, because
    that means the stored data is corrupt and silently skipping it would make
    the totals lie.
    """
    by_status = {status: 0 for status in STATUSES}
    by_priority = {priority: 0 for priority in PRIORITIES}

    for ticket in tickets:
        status = ticket.get("status")
        priority = ticket.get("priority")
        if status not in by_status:
            raise ValueError(
                f"Ticket {ticket.get('id')} has unknown status '{status}'."
            )
        if priority not in by_priority:
            raise ValueError(
                f"Ticket {ticket.get('id')} has unknown priority '{priority}'."
            )
        by_status[status] += 1
        by_priority[priority] += 1

    return {
        "total": len(tickets),
        "by_status": by_status,
        "by_priority": by_priority,
    }


def format_report(report):
    """Turn a report dict into printable text for the CLI."""
    lines = [f"Total tickets: {report['total']}", "", "By status:"]
    for status, count in report["by_status"].items():
        lines.append(f"  {status}: {count}")
    lines.append("")
    lines.append("By priority:")
    for priority, count in report["by_priority"].items():
        lines.append(f"  {priority}: {count}")
    return "\n".join(lines)
