"""CLI-level regression tests for report metrics and workflow changes."""

import inspect
import os
import tempfile
import unittest

from campusflow.cli import run


def drive(answers, path):
    """Run a scripted CLI session, authenticating when that feature is present."""
    output = []
    run_options = {}

    if "users_path" in inspect.signature(run).parameters:
        from campusflow.auth import create_user, save_users

        users_path = path + ".users.json"
        password = "CampusFlowTestPassword123!"
        if not os.path.exists(users_path):
            users = []
            create_user(users, "testuser", password)
            save_users(users, users_path)
        answers = ["testuser", *answers]
        run_options = {
            "password_fn": lambda prompt="": password,
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


class TestReportCli(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.path = os.path.join(self.folder.name, "tickets.json")

    def test_report_cli_shows_breakdowns_and_tracks_resolve_reopen(self):
        code, out = drive(
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

        self.assertEqual(code, 0)
        self.assertIn("By status:", out)
        self.assertIn("By priority:", out)
        self.assertIn("By category:", out)
        self.assertIn("Network: 1", out)
        self.assertIn("Hardware: 1", out)
        self.assertIn("Resolution percentage: 50%", out)
        self.assertIn("Resolution percentage: 0%", out)
        self.assertIn("T001 reopened.", out)


if __name__ == "__main__":
    unittest.main()
