"""Regression tests for Issue #1 validation and lifecycle guarantees."""

import copy
import unittest

from campusflow.tickets import assign_ticket, create_ticket
from campusflow.workflow import change_status, find_ticket, reopen_ticket


def ticket(ticket_id="T001", status="open", assigned_to=None):
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


class TestTicketIdValidation(unittest.TestCase):
    def test_valid_id_is_normalized(self):
        self.assertEqual(find_ticket([ticket()], " t001 ")["id"], "T001")

    def test_malformed_ids_are_rejected_separately_from_unknown_ids(self):
        for bad_id in ("", "  ", "T", "ABC", "T-1", "T1A", None, 1, True):
            with self.subTest(ticket_id=bad_id):
                with self.assertRaises(ValueError):
                    find_ticket([ticket()], bad_id)

    def test_valid_but_unknown_id_has_unknown_message(self):
        with self.assertRaisesRegex(ValueError, "Unknown ticket ID"):
            find_ticket([ticket()], "T999")


class TestFailedActionsPreserveCompleteState(unittest.TestCase):
    def test_invalid_creation_does_not_change_collection(self):
        cases = (
            {"title": "   "},
            {"category": "Plumbing"},
            {"urgency": "urgent"},
            {"affected_users": True},
            {"affected_users": 1.5},
            {"affected_users": "15"},
            {"affected_users": "many"},
            {"affected_users": 0},
            {"affected_users": -1},
        )
        for invalid in cases:
            with self.subTest(invalid=invalid):
                tickets = [ticket()]
                before = copy.deepcopy(tickets)
                values = {
                    "title": "New issue",
                    "category": "Network",
                    "urgency": "medium",
                    "affected_users": 2,
                }
                values.update(invalid)
                with self.assertRaises(ValueError):
                    create_ticket(tickets, **values)
                self.assertEqual(tickets, before)

    def test_failed_assignment_preserves_entire_resolved_ticket(self):
        tickets = [ticket(status="resolved", assigned_to="Amina")]
        before = copy.deepcopy(tickets)
        with self.assertRaises(ValueError):
            assign_ticket(tickets, "T001", "Chidi")
        self.assertEqual(tickets, before)

    def test_invalid_transition_preserves_entire_collection(self):
        tickets = [
            ticket(status="open", assigned_to=None),
            ticket("T002", status="in_progress", assigned_to="Amina"),
        ]
        before = copy.deepcopy(tickets)
        with self.assertRaises(ValueError):
            change_status(tickets, "T001", "in_progress")
        self.assertEqual(tickets, before)

    def test_blank_assignment_name_preserves_entire_collection(self):
        tickets = [ticket(assigned_to="Amina")]
        before = copy.deepcopy(tickets)
        with self.assertRaises(ValueError):
            assign_ticket(tickets, "T001", "   ")
        self.assertEqual(tickets, before)

    def test_malformed_id_during_assignment_preserves_collection(self):
        tickets = [ticket()]
        before = copy.deepcopy(tickets)
        with self.assertRaises(ValueError):
            assign_ticket(tickets, "T-1", "Amina")
        self.assertEqual(tickets, before)

    def test_reopen_of_non_resolved_ticket_preserves_collection(self):
        tickets = [ticket(status="open")]
        before = copy.deepcopy(tickets)
        with self.assertRaises(ValueError):
            reopen_ticket(tickets, "T001")
        self.assertEqual(tickets, before)


if __name__ == "__main__":
    unittest.main()
