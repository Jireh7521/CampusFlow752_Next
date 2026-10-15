import os
import tempfile
import unittest

from campusflow.cli import run
from campusflow.storage import load_tickets


def drive(answers, path):
    """Run a menu session with scripted input, including auth when available."""
    output = []
    run_options = {}

    # This test branch can be tested against main before auth is merged, and
    # against the integrated application after the authentication PR is merged.
    if "users_path" in __import__("inspect").signature(run).parameters:
        from campusflow.auth import create_user, save_users

        users_path = path + ".users.json"
        test_password = "CampusFlowTestPassword123!"
        if not os.path.exists(users_path):
            users = []
            create_user(users, "testuser", test_password)
            save_users(users, users_path)
        answers = ["testuser", *answers]
        run_options = {
            "password_fn": lambda prompt="": test_password,
            "users_path": users_path,
        }

    remaining = iter(answers)

    def fake_input(prompt=""):
        try:
            return next(remaining)
        except StopIteration:
            raise EOFError

    code = run(
        input_fn=fake_input,
        print_fn=output.append,
        path=path,
        **run_options,
    )
    return code, "\n".join(output)

class TestCli(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.path = os.path.join(self.folder.name, "tickets.json")

    def test_full_demo_route(self):
        code, out = drive(
            [
                "1", "Campus Wi-Fi is down", "network", "high", "15",
                "1", "Bad ticket", "network", "high", "0",
                "1", "Slow printer", "hardware", "low", "1",
                "5", "T001", "in_progress",
                "4", "T001", "Amina",
                "5", "T001", "in_progress",
                "5", "T001", "open",
                "5", "T001", "resolved",
                "7",
                "8",
                "0",
            ],
            self.path,
        )
        self.assertEqual(code, 0)
        self.assertIn("Created T001 with priority 'critical'", out)
        self.assertIn("Affected users must be a positive whole number", out)
        self.assertIn("is unassigned", out)
        self.assertIn("Invalid transition", out)
        self.assertIn("T001 is now resolved", out)
        self.assertIn("Total tickets: 2", out)

        saved = load_tickets(self.path)
        self.assertEqual([t["id"] for t in saved], ["T001", "T002"])
        self.assertEqual(saved[0]["status"], "resolved")

    def test_data_survives_restart_and_ids_stay_unique(self):
        drive(["1", "First", "other", "low", "1", "0"], self.path)
        _, out = drive(["1", "Second", "other", "low", "1", "2", "0"], self.path)
        self.assertIn("Loaded 1 ticket(s)", out)
        self.assertIn("Created T002", out)

    def test_corrupted_file_stops_startup_and_is_not_overwritten(self):
        with open(self.path, "w", encoding="utf-8") as handle:
            handle.write("not json at all")
        code, out = drive(["1", "x", "other", "low", "1", "0"], self.path)
        self.assertEqual(code, 1)
        self.assertIn("not valid JSON", out)
        with open(self.path, encoding="utf-8") as handle:
            self.assertEqual(handle.read(), "not json at all")

    def test_invalid_menu_choice_and_empty_views(self):
        _, out = drive(["99", "2", "7", "8", "0"], self.path)
        self.assertIn("Invalid choice", out)
        self.assertIn("No tickets yet.", out)
        self.assertIn("The work queue is empty.", out)
        self.assertIn("Total tickets: 0", out)

    def test_failed_action_does_not_corrupt_saved_tickets(self):
        drive(["1", "Only", "other", "low", "1", "0"], self.path)
        before = load_tickets(self.path)
        drive(["4", "T999", "Amina", "5", "T001", "resolved", "0"], self.path)
        self.assertEqual(load_tickets(self.path), before)

    def test_reopen_flow(self):
        _, out = drive(
            [
                "1", "Issue", "other", "low", "1",
                "4", "T001", "Amina",
                "5", "T001", "in_progress",
                "5", "T001", "resolved",
                "4", "T001", "Bola",
                "6", "T001",
                "4", "T001", "Bola",
                "0",
            ],
            self.path,
        )
        self.assertIn("is resolved and cannot be modified", out)
        self.assertIn("T001 reopened.", out)
        self.assertIn("T001 assigned to Bola.", out)

    def test_add_follow_up_note_is_saved_and_shown_in_ticket_view(self):
        _, out = drive(
            [
                "1", "Wi-Fi issue", "network", "high", "5",
                "9", "T001", "Amina", "Checked the router.",
                "3", "T001",
                "0",
            ],
            self.path,
        )
        self.assertIn("Added note to T001.", out)
        self.assertIn("N001 | Amina: Checked the router.", out)
        saved = load_tickets(self.path)
        self.assertEqual(saved[0]["notes"][0]["note_id"], "N001")

    def test_search_tickets_from_menu(self):
        _, out = drive(
            [
                "1", "Campus Wi-Fi is down", "network", "high", "15",
                "10", "campus", "", "", "",
                "0",
            ],
            self.path,
        )
        self.assertIn("T001", out)
        self.assertIn("Campus Wi-Fi is down", out)
        self.assertIn("Search tickets", out)

    def test_search_reprompts_after_invalid_filter_and_shows_columns(self):
        _, out = drive(
            [
                "1", "Campus Wi-Fi is down", "network", "high", "15",
                "10", "campus", "plumbing", "NETWORK", "", "",
                "0",
            ],
            self.path,
        )
        self.assertIn("Invalid category filter", out)
        self.assertIn("ID", out)
        self.assertIn("Title", out)
        self.assertIn("Category", out)
        self.assertIn("Priority", out)
        self.assertIn("Status", out)
        self.assertIn("Assignee", out)
        self.assertIn("Campus Wi-Fi is down", out)

    def test_priority_sorted_search_is_separate_from_work_queue(self):
        _, out = drive(
            [
                "1", "First low priority", "other", "low", "1",
                "1", "Second critical priority", "network", "high", "15",
                "11", "", "", "", "",
                "7",
                "0",
            ],
            self.path,
        )
        self.assertIn("11. Search tickets (priority sorted)", out)
        self.assertIn("7. Work queue", out)
        self.assertLess(
            out.index("T002 | Second critical priority"),
            out.index("T001 | First low priority"),
        )

    def test_report_cli_shows_breakdowns_and_tracks_resolve_reopen(self):
        _, out = drive(
            [
                "1", "Campus Wi-Fi", "network", "high", "15",
                "1", "Printer fault", "hardware", "low", "1",
                "4", "T001", "Amina",
                "5", "T001", "in_progress",
                "5", "T001", "resolved",
                "8",
                "6", "T001",
                "8",
                "0",
            ],
            self.path,
        )

        self.assertIn("By status:", out)
        self.assertIn("By priority:", out)
        self.assertIn("By category:", out)
        self.assertIn("Network: 1", out)
        self.assertIn("Hardware: 1", out)
        self.assertIn("Resolution percentage: 50%", out)
        self.assertIn("Resolution percentage: 0%", out)
        self.assertIn("T001 reopened.", out)

    def test_exit_on_closed_input(self):
        code, _ = drive([], self.path)
        self.assertEqual(code, 0)


if __name__ == "__main__":
    unittest.main()
