import unittest

from campusflow.tickets import (
    assign_ticket,
    calculate_priority,
    create_ticket,
    format_ticket,
    format_ticket_list,
    next_ticket_id,
    normalize_category,
    normalize_urgency,
    validate_affected_users,
)


def new_ticket(tickets, **overrides):
    values = {
        "title": "Campus Wi-Fi is down",
        "category": "Network",
        "urgency": "high",
        "affected_users": 15,
    }
    values.update(overrides)
    return create_ticket(tickets, **values)


class TestPriority(unittest.TestCase):
    def test_high_urgency_and_12_users_is_critical(self):
        self.assertEqual(calculate_priority("high", 12), "critical")

    def test_high_urgency_and_2_users_is_high(self):
        self.assertEqual(calculate_priority("high", 2), "high")

    def test_low_urgency_and_4_users_is_medium(self):
        self.assertEqual(calculate_priority("low", 4), "medium")

    def test_low_urgency_and_1_user_is_low(self):
        self.assertEqual(calculate_priority("low", 1), "low")

    def test_boundaries(self):
        self.assertEqual(calculate_priority("high", 10), "critical")
        self.assertEqual(calculate_priority("high", 9), "high")
        self.assertEqual(calculate_priority("low", 10), "high")
        self.assertEqual(calculate_priority("low", 9), "medium")
        self.assertEqual(calculate_priority("low", 3), "medium")
        self.assertEqual(calculate_priority("low", 2), "low")
        self.assertEqual(calculate_priority("medium", 1), "medium")
        self.assertEqual(calculate_priority("medium", 10), "high")

    def test_priority_accepts_case_variations(self):
        self.assertEqual(calculate_priority("HIGH", 12), "critical")


class TestValidation(unittest.TestCase):
    def test_zero_affected_users_rejected(self):
        with self.assertRaises(ValueError):
            validate_affected_users(0)
        tickets = []
        with self.assertRaises(ValueError):
            new_ticket(tickets, affected_users=0)
        self.assertEqual(tickets, [])

    def test_bad_affected_users_rejected(self):
        for bad in (-3, "-3", 2.5, "2.5", "15", "many", "", None, True):
            with self.subTest(value=bad):
                with self.assertRaises(ValueError):
                    validate_affected_users(bad)

    def test_string_affected_users_are_rejected(self):
        with self.assertRaises(ValueError):
            validate_affected_users("15")

    def test_blank_title_rejected(self):
        tickets = []
        for bad in ("", "   ", None):
            with self.subTest(title=bad):
                with self.assertRaises(ValueError):
                    new_ticket(tickets, title=bad)
        self.assertEqual(tickets, [])

    def test_invalid_urgency_and_category_rejected(self):
        tickets = []
        with self.assertRaises(ValueError):
            new_ticket(tickets, urgency="urgent")
        with self.assertRaises(ValueError):
            new_ticket(tickets, category="Plumbing")
        self.assertEqual(tickets, [])

    def test_case_variations_are_normalized(self):
        self.assertEqual(normalize_category("  nEtWoRk "), "Network")
        self.assertEqual(normalize_urgency(" HIGH "), "high")


class TestCreateTicket(unittest.TestCase):
    def test_created_ticket_has_all_fields_and_defaults(self):
        tickets = []
        ticket = new_ticket(tickets, category="network", urgency="HIGH")
        self.assertEqual(
            ticket,
            {
                "id": "T001",
                "title": "Campus Wi-Fi is down",
                "category": "Network",
                "urgency": "high",
                "affected_users": 15,
                "priority": "critical",
                "status": "open",
                "assigned_to": None,
            },
        )
        self.assertEqual(tickets, [ticket])

    def test_ids_are_sequential_and_unique(self):
        tickets = []
        ids = [new_ticket(tickets)["id"] for _ in range(3)]
        self.assertEqual(ids, ["T001", "T002", "T003"])

    def test_next_id_follows_highest_existing_id(self):
        tickets = [{"id": "T001"}, {"id": "T005"}]
        self.assertEqual(next_ticket_id(tickets), "T006")
        self.assertEqual(next_ticket_id([]), "T001")


class TestAssign(unittest.TestCase):
    def test_assign_sets_name(self):
        tickets = []
        new_ticket(tickets)
        result = assign_ticket(tickets, "T001", "  Amina ")
        self.assertEqual(result["assigned_to"], "Amina")

    def test_unknown_ticket_id_rejected(self):
        with self.assertRaises(ValueError):
            assign_ticket([], "T001", "Amina")

    def test_blank_name_rejected_and_ticket_unchanged(self):
        tickets = []
        new_ticket(tickets)
        with self.assertRaises(ValueError):
            assign_ticket(tickets, "T001", "   ")
        self.assertIsNone(tickets[0]["assigned_to"])

    def test_resolved_ticket_cannot_be_assigned_until_reopened(self):
        tickets = []
        new_ticket(tickets)
        tickets[0]["status"] = "resolved"
        with self.assertRaises(ValueError):
            assign_ticket(tickets, "T001", "Amina")
        self.assertIsNone(tickets[0]["assigned_to"])


class TestFormatting(unittest.TestCase):
    def test_empty_list_message(self):
        self.assertEqual(format_ticket_list([]), "No tickets yet.")

    def test_view_and_list_show_ticket_details(self):
        tickets = []
        new_ticket(tickets)
        self.assertIn("Campus Wi-Fi is down", format_ticket(tickets[0]))
        self.assertIn("(unassigned)", format_ticket(tickets[0]))
        self.assertIn("T001", format_ticket_list(tickets))


if __name__ == "__main__":
    unittest.main()
