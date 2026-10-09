import unittest

from campusflow.work_queue import get_work_queue, ticket_number


def make_ticket(ticket_id, priority="low", status="open"):
    return {
        "id": ticket_id,
        "title": f"Ticket {ticket_id}",
        "category": "Other",
        "urgency": "low",
        "affected_users": 1,
        "priority": priority,
        "status": status,
        "assigned_to": None,
    }


def ids(tickets):
    return [t["id"] for t in tickets]


class TestWorkQueue(unittest.TestCase):
    def test_queue_sorted_by_priority(self):
        tickets = [
            make_ticket("T001", "low"),
            make_ticket("T002", "critical"),
            make_ticket("T003", "medium"),
            make_ticket("T004", "high"),
        ]
        self.assertEqual(
            ids(get_work_queue(tickets)), ["T002", "T004", "T003", "T001"]
        )

    def test_priority_ties_broken_by_earlier_ticket_id(self):
        tickets = [
            make_ticket("T003", "high"),
            make_ticket("T001", "high"),
            make_ticket("T002", "high"),
        ]
        self.assertEqual(ids(get_work_queue(tickets)), ["T001", "T002", "T003"])

    def test_tie_break_uses_number_not_string(self):
        # As strings "T10" < "T2"; as numbers 2 < 10.
        tickets = [make_ticket("T10", "high"), make_ticket("T2", "high")]
        self.assertEqual(ids(get_work_queue(tickets)), ["T2", "T10"])

    def test_only_open_tickets_are_queued(self):
        tickets = [
            make_ticket("T001", "critical", status="open"),
            make_ticket("T002", "critical", status="in_progress"),
            make_ticket("T003", "critical", status="resolved"),
        ]
        self.assertEqual(ids(get_work_queue(tickets)), ["T001"])

    def test_empty_inputs_give_empty_queue(self):
        self.assertEqual(get_work_queue([]), [])
        self.assertEqual(
            get_work_queue([make_ticket("T001", status="resolved")]), []
        )

    def test_input_list_is_not_modified(self):
        tickets = [make_ticket("T001", "low"), make_ticket("T002", "critical")]
        original_order = ids(tickets)
        get_work_queue(tickets)
        self.assertEqual(ids(tickets), original_order)

    def test_unknown_priority_rejected(self):
        with self.assertRaises(ValueError):
            get_work_queue([make_ticket("T001", "urgent")])

    def test_ticket_number_parsing(self):
        self.assertEqual(ticket_number({"id": "T010"}), 10)
        with self.assertRaises(ValueError):
            ticket_number({"id": "ABC"})


if __name__ == "__main__":
    unittest.main()
