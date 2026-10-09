import unittest

from campusflow.reports import build_report, format_report


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


class TestReports(unittest.TestCase):
    def test_empty_report_has_zero_total_and_all_zero_counts(self):
        report = build_report([])
        self.assertEqual(report["total"], 0)
        self.assertEqual(
            report["by_status"], {"open": 0, "in_progress": 0, "resolved": 0}
        )
        self.assertEqual(
            report["by_priority"],
            {"critical": 0, "high": 0, "medium": 0, "low": 0},
        )

    def test_mixed_tickets_are_counted_correctly(self):
        tickets = [
            make_ticket("T001", "critical", "open"),
            make_ticket("T002", "critical", "resolved"),
            make_ticket("T003", "high", "in_progress"),
            make_ticket("T004", "low", "open"),
            make_ticket("T005", "low", "open"),
        ]
        report = build_report(tickets)
        self.assertEqual(report["total"], 5)
        self.assertEqual(
            report["by_status"], {"open": 3, "in_progress": 1, "resolved": 1}
        )
        self.assertEqual(
            report["by_priority"],
            {"critical": 2, "high": 1, "medium": 0, "low": 2},
        )

    def test_breakdowns_add_up_to_total(self):
        tickets = [make_ticket(f"T{i:03d}", "medium") for i in range(1, 8)]
        report = build_report(tickets)
        self.assertEqual(sum(report["by_status"].values()), report["total"])
        self.assertEqual(sum(report["by_priority"].values()), report["total"])

    def test_unknown_status_or_priority_rejected(self):
        with self.assertRaises(ValueError):
            build_report([make_ticket("T001", status="closed")])
        with self.assertRaises(ValueError):
            build_report([make_ticket("T001", priority="urgent")])

    def test_format_report_shows_totals_and_zero_rows(self):
        text = format_report(build_report([]))
        self.assertIn("Total tickets: 0", text)
        self.assertIn("in_progress: 0", text)
        self.assertIn("critical: 0", text)


if __name__ == "__main__":
    unittest.main()
