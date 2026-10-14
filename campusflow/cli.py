"""Text menu for CampusFlow.

run() takes input_fn / print_fn so tests can drive the whole menu with
scripted answers instead of a real keyboard.
"""

from campusflow.reports import build_report, format_report
from campusflow.storage import DEFAULT_PATH, StorageError, load_tickets, save_tickets
from campusflow.tickets import (
    assign_ticket,
    create_ticket,
    format_ticket,
    format_ticket_list,
    parse_affected_users_input,
)
from campusflow.work_queue import get_work_queue
from campusflow.workflow import change_status, find_ticket, reopen_ticket

MENU = """
=== CampusFlow ===
1. Create ticket
2. List all tickets
3. View one ticket
4. Assign ticket
5. Change ticket status
6. Reopen resolved ticket
7. Work queue
8. Report
0. Exit"""


def run(input_fn=input, print_fn=print, path=DEFAULT_PATH):
    """Run the menu until Exit. Returns 0 on normal exit, 1 if data is unsafe."""
    try:
        tickets = load_tickets(path)
    except StorageError as error:
        print_fn(f"Error: {error}")
        print_fn("CampusFlow will not start, so your data is not overwritten.")
        return 1

    print_fn(f"Loaded {len(tickets)} ticket(s).")

    while True:
        print_fn(MENU)
        try:
            choice = input_fn("Choose an option: ").strip()
        except EOFError:
            print_fn("\nInput closed. Goodbye.")
            return 0

        if choice == "0":
            print_fn("Goodbye.")
            return 0

        try:
            changed = _handle(choice, tickets, input_fn, print_fn)
            if changed:
                save_tickets(tickets, path)
        except ValueError as error:
            print_fn(f"Error: {error}")
        except OSError as error:
            print_fn(f"Error: could not save tickets: {error}")


def _handle(choice, tickets, input_fn, print_fn):
    """Run one menu action. Returns True if tickets changed and need saving."""
    if choice == "1":
        ticket = create_ticket(
            tickets,
            input_fn("Title: "),
            input_fn("Category (Network/Hardware/Software/Other): "),
            input_fn("Urgency (low/medium/high): "),
            parse_affected_users_input(input_fn("Affected users: ")),
        )
        print_fn(
            f"Created {ticket['id']} with priority '{ticket['priority']}'."
        )
        return True

    if choice == "2":
        print_fn(format_ticket_list(tickets))
        return False

    if choice == "3":
        print_fn(format_ticket(find_ticket(tickets, input_fn("Ticket ID: "))))
        return False

    if choice == "4":
        ticket = assign_ticket(
            tickets, input_fn("Ticket ID: "), input_fn("Staff member name: ")
        )
        print_fn(f"{ticket['id']} assigned to {ticket['assigned_to']}.")
        return True

    if choice == "5":
        ticket = change_status(
            tickets,
            input_fn("Ticket ID: "),
            input_fn("New status (in_progress/resolved): "),
        )
        print_fn(f"{ticket['id']} is now {ticket['status']}.")
        return True

    if choice == "6":
        ticket = reopen_ticket(tickets, input_fn("Ticket ID: "))
        print_fn(f"{ticket['id']} reopened.")
        return True

    if choice == "7":
        queue = get_work_queue(tickets)
        if not queue:
            print_fn("The work queue is empty.")
        else:
            print_fn(format_ticket_list(queue))
        return False

    if choice == "8":
        print_fn(format_report(build_report(tickets)))
        return False

    print_fn("Invalid choice. Enter a number from the menu.")
    return False
