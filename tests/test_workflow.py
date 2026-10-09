import unittest

from campusflow.workflow import (
    change_status,
    ensure_modifiable,
    find_ticket,
    reopen_ticket,
)


def make_ticket(ticket_id="T001", status="open", assigned_to=None):
    return {
        "id": ticket_id,
        "title": "Campus Wi-Fi is down",
        "category": "Network",
        "urgency": "high",
        "affected_users": 15,
        "priority": "critical",
        "status": status,
        "assigned_to": assigned_to,
    }


class TestChangeStatus(unittest.TestCase):
    def test_unassigned_ticket_cannot_move_to_in_progress(self):
        tickets = [make_ticket()]
        with self.assertRaises(ValueError):
            change_status(tickets, "T001", "in_progress")
        self.assertEqual(tickets[0]["status"], "open")

    def test_blank_assignee_counts_as_unassigned(self):
        tickets = [make_ticket(assigned_to="   ")]
        with self.assertRaises(ValueError):
            change_status(tickets, "T001", "in_progress")

    def test_assigned_ticket_progresses_open_to_resolved(self):
        tickets = [make_ticket(assigned_to="Amina")]
        result = change_status(tickets, "T001", "in_progress")
        self.assertEqual(result["status"], "in_progress")
        result = change_status(tickets, "T001", "resolved")
        self.assertEqual(result["status"], "resolved")
        self.assertEqual(tickets[0]["status"], "resolved")

    def test_cannot_skip_in_progress(self):
        tickets = [make_ticket(assigned_to="Amina")]
        with self.assertRaises(ValueError):
            change_status(tickets, "T001", "resolved")
        self.assertEqual(tickets[0]["status"], "open")

    def test_cannot_move_backwards_from_in_progress(self):
        tickets = [make_ticket(status="in_progress", assigned_to="Amina")]
        with self.assertRaises(ValueError):
            change_status(tickets, "T001", "open")
        self.assertEqual(tickets[0]["status"], "in_progress")

    def test_resolved_ticket_cannot_move_to_in_progress(self):
        tickets = [make_ticket(status="resolved", assigned_to="Amina")]
        with self.assertRaises(ValueError):
            change_status(tickets, "T001", "in_progress")
        self.assertEqual(tickets[0]["status"], "resolved")

    def test_unknown_ticket_id_rejected(self):
        with self.assertRaises(ValueError):
            change_status([make_ticket()], "T999", "in_progress")

    def test_invalid_status_name_rejected_and_ticket_unchanged(self):
        tickets = [make_ticket(assigned_to="Amina")]
        before = dict(tickets[0])
        with self.assertRaises(ValueError):
            change_status(tickets, "T001", "done")
        self.assertEqual(tickets[0], before)

    def test_ticket_id_and_status_case_are_normalized(self):
        tickets = [make_ticket(assigned_to="Amina")]
        result = change_status(tickets, " t001 ", "IN_PROGRESS")
        self.assertEqual(result["status"], "in_progress")


class TestReopen(unittest.TestCase):
    def test_reopen_sets_resolved_ticket_to_open(self):
        tickets = [make_ticket(status="resolved", assigned_to="Amina")]
        result = reopen_ticket(tickets, "T001")
        self.assertEqual(result["status"], "open")
        self.assertEqual(result["assigned_to"], "Amina")

    def test_reopen_rejects_ticket_that_is_not_resolved(self):
        tickets = [make_ticket(status="open")]
        with self.assertRaises(ValueError):
            reopen_ticket(tickets, "T001")

    def test_reopened_ticket_can_progress_again(self):
        tickets = [make_ticket(status="resolved", assigned_to="Amina")]
        reopen_ticket(tickets, "T001")
        change_status(tickets, "T001", "in_progress")
        self.assertEqual(tickets[0]["status"], "in_progress")

    def test_change_status_to_open_also_reopens_resolved(self):
        tickets = [make_ticket(status="resolved", assigned_to="Amina")]
        change_status(tickets, "T001", "open")
        self.assertEqual(tickets[0]["status"], "open")


class TestModifiableGuard(unittest.TestCase):
    def test_resolved_ticket_is_not_modifiable(self):
        with self.assertRaises(ValueError):
            ensure_modifiable(make_ticket(status="resolved"))

    def test_open_and_in_progress_tickets_are_modifiable(self):
        ensure_modifiable(make_ticket(status="open"))
        ensure_modifiable(make_ticket(status="in_progress"))


class TestFindTicket(unittest.TestCase):
    def test_blank_id_rejected(self):
        with self.assertRaises(ValueError):
            find_ticket([make_ticket()], "  ")


if __name__ == "__main__":
    unittest.main()
