import unittest

from campusflow.reports import build_report, format_report
from campusflow.workflow import change_status, reopen_ticket


def make_ticket(
    ticket_id,
    priority="low",
    status="open",
    category="Other",
    assigned_to=None,
):
    return {
        "id": ticket_id,
        "title": f"Ticket {ticket_id}",
        "category": category,
        "urgency": "low",
        "affected_users": 1,
        "priority": priority,
        "status": status,
        "assigned_to": assigned_to,
    }


class TestReports(unittest.TestCase):
    def test_empty_report_has_zero_totals_metrics_and_all_zero_counts(self):
        report = build_report([])
        self.assertEqual(report["total"], 0)
        self.assertEqual(
            report["by_status"],
            {"open": 0, "in_progress": 0, "resolved": 0},
        )
        self.assertEqual(
            report["by_priority"],
            {"critical": 0, "high": 0, "medium": 0, "low": 0},
        )
        self.assertEqual(
            report["by_category"],
            {"Network": 0, "Hardware": 0, "Software": 0, "Other": 0},
        )
        self.assertEqual(report["unresolved"], 0)
        self.assertEqual(report["resolved"], 0)
        self.assertEqual(report["resolution_percentage"], 0)

    def test_known_fixture_counts_totals_and_breakdowns(self):
        tickets = [
            make_ticket("T001", "critical", "open", "Network"),
            make_ticket("T002", "critical", "resolved", "Network"),
            make_ticket("T003", "high", "in_progress", "Hardware", "Amina"),
            make_ticket("T004", "low", "open", "Other"),
            make_ticket("T005", "low", "open", "Other"),
        ]

        report = build_report(tickets)

        self.assertEqual(report["total"], 5)
        self.assertEqual(
            report["by_status"],
            {"open": 3, "in_progress": 1, "resolved": 1},
        )
        self.assertEqual(
            report["by_priority"],
            {"critical": 2, "high": 1, "medium": 0, "low": 2},
        )
        self.assertEqual(
            report["by_category"],
            {"Network": 2, "Hardware": 1, "Software": 0, "Other": 2},
        )
        self.assertEqual(report["unresolved"], 4)
        self.assertEqual(report["resolved"], 1)
        self.assertAlmostEqual(report["resolution_percentage"], 20.0)

    def test_metrics_follow_resolve_and_reopen_operations(self):
        tickets = [
            make_ticket("T001", "high", "in_progress", "Network", "Amina"),
            make_ticket("T002", "medium", "open", "Software"),
            make_ticket("T003", "low", "resolved", "Other", "Bola"),
        ]

        before = build_report(tickets)
        self.assertEqual(before["total"], 3)
        self.assertEqual(before["unresolved"], 2)
        self.assertEqual(before["resolved"], 1)
        self.assertAlmostEqual(before["resolution_percentage"], 100 / 3)
        self.assertEqual(sum(before["by_status"].values()), before["total"])

        change_status(tickets, "T001", "resolved")
        after_resolve = build_report(tickets)
        self.assertEqual(after_resolve["by_status"], {
            "open": 1, "in_progress": 0, "resolved": 2
        })
        self.assertEqual(after_resolve["unresolved"], 1)
        self.assertEqual(after_resolve["resolved"], 2)
        self.assertAlmostEqual(after_resolve["resolution_percentage"], 200 / 3)
        self.assertEqual(sum(after_resolve["by_status"].values()), 3)

        reopen_ticket(tickets, "T003")
        after_reopen = build_report(tickets)
        self.assertEqual(after_reopen["by_status"], {
            "open": 2, "in_progress": 0, "resolved": 1
        })
        self.assertEqual(after_reopen["unresolved"], 2)
        self.assertEqual(after_reopen["resolved"], 1)
        self.assertAlmostEqual(after_reopen["resolution_percentage"], 100 / 3)
        self.assertEqual(sum(after_reopen["by_status"].values()), 3)

    def test_breakdowns_add_up_to_total(self):
        tickets = [
            make_ticket(f"T{i:03d}", "medium", category="Hardware")
            for i in range(1, 8)
        ]
        report = build_report(tickets)
        self.assertEqual(sum(report["by_status"].values()), report["total"])
        self.assertEqual(sum(report["by_priority"].values()), report["total"])
        self.assertEqual(sum(report["by_category"].values()), report["total"])

    def test_unknown_status_priority_or_category_rejected(self):
        with self.assertRaises(ValueError):
            build_report([make_ticket("T001", status="closed")])
        with self.assertRaises(ValueError):
            build_report([make_ticket("T001", priority="urgent")])
        with self.assertRaises(ValueError):
            build_report([make_ticket("T001", category="Plumbing")])

    def test_format_report_shows_all_metrics_and_zero_rows(self):
        text = format_report(build_report([]))
        self.assertIn("Total tickets: 0", text)
        self.assertIn("in_progress: 0", text)
        self.assertIn("critical: 0", text)
        self.assertIn("Software: 0", text)
        self.assertIn("Unresolved tickets: 0", text)
        self.assertIn("Resolved tickets: 0", text)
        self.assertIn("Resolution percentage: 0%", text)


if __name__ == "__main__":
    unittest.main()
