import os
import tempfile
import unittest

from campusflow.cli import run


def drive(answers, path):
    """Run the CLI with scripted input and a temporary account when auth exists."""
    output = []
    run_options = {}

    # Keep this test runnable against both the current main branch and the
    # integrated CLI after the authentication PR is merged.
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
    return code, "\\n".join(output)

class TestSearchCli(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.path = os.path.join(self.folder.name, "tickets.json")

    def test_combined_search_filters_match_only_one_ticket(self):
        _, out = drive(
            [
                "1", "Campus Wi-Fi outage", "network", "high", "15",
                "1", "Campus Wi-Fi printer", "hardware", "low", "1",
                "4", "T001", "Amina",
                "5", "T001", "in_progress",
                "10", "campus", "Network", "in_progress", "critical",
                "0",
            ],
            self.path,
        )
        self.assertIn("Campus Wi-Fi outage", out)
        self.assertNotIn("Campus Wi-Fi printer", out)

    def test_invalid_status_and_priority_filters_reprompt(self):
        _, out = drive(
            [
                "1", "Campus Wi-Fi outage", "network", "high", "15",
                "4", "T001", "Amina",
                "5", "T001", "in_progress",
                "10", "campus", "", "waiting", "IN_PROGRESS",
                "urgent", "CRITICAL",
                "0",
            ],
            self.path,
        )
        self.assertIn("Invalid status filter", out)
        self.assertIn("Invalid priority filter", out)
        self.assertIn("Campus Wi-Fi outage", out)


if __name__ == "__main__":
    unittest.main()
