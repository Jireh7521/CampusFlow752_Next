"""Integration tests for the local CampusFlow web interface."""
import http.client
import json
import tempfile
import threading
import unittest
from pathlib import Path

from campusflow.web import create_server


class CampusFlowWebTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        self.server = create_server(
            port=0,
            tickets_path=str(root / "tickets.json"),
            users_path=str(root / "users.json"),
        )
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.connection = http.client.HTTPConnection(
            "127.0.0.1", self.server.server_address[1]
        )
        self.cookie = ""
        self.csrf = ""

    def tearDown(self):
        self.connection.close()
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)
        self.temp.cleanup()

    def request_json(self, method, path, payload=None, csrf=True):
        body = json.dumps(payload or {})
        headers = {"Content-Type": "application/json"}
        if self.cookie:
            headers["Cookie"] = self.cookie
        if csrf and self.csrf and method != "GET":
            headers["X-CSRF-Token"] = self.csrf
        self.connection.request(method, path, body=body, headers=headers)
        response = self.connection.getresponse()
        raw = response.read()
        if response.getheader("Set-Cookie"):
            self.cookie = response.getheader("Set-Cookie").split(";", 1)[0]
        data = json.loads(raw) if raw else {}
        return response.status, data

    def sign_in_first_account(self):
        status, session = self.request_json("GET", "/api/session")
        self.assertEqual(status, 200)
        self.csrf = session["csrfToken"]
        self.assertTrue(session["setupRequired"])
        status, data = self.request_json(
            "POST",
            "/api/auth/setup",
            {"username": "webtester", "password": "a-strong-test-password"},
        )
        self.assertEqual(status, 200, data)
        self.assertEqual(data["username"], "webtester")
        self.csrf = data["csrfToken"]

    def test_setup_create_ticket_and_read_dashboard_data(self):
        self.sign_in_first_account()
        status, result = self.request_json(
            "POST",
            "/api/tickets",
            {
                "title": "Library Wi-Fi unavailable",
                "category": "Network",
                "urgency": "high",
                "affected_users": 12,
            },
        )
        self.assertEqual(status, 200, result)
        self.assertEqual(result["ticket"]["id"], "T001")
        self.assertEqual(result["ticket"]["priority"], "critical")

        status, result = self.request_json("GET", "/api/tickets")
        self.assertEqual(status, 200)
        self.assertEqual(len(result["tickets"]), 1)

        status, report = self.request_json("GET", "/api/reports")
        self.assertEqual(status, 200)
        self.assertEqual(report["total"], 1)
        self.assertEqual(report["by_priority"]["critical"], 1)

    def test_ticket_api_requires_authentication(self):
        status, session = self.request_json("GET", "/api/session")
        self.assertEqual(status, 200)
        self.csrf = session["csrfToken"]
        status, result = self.request_json("GET", "/api/tickets")
        self.assertEqual(status, 401)
        self.assertIn("sign in", result["error"].lower())

    def test_mutating_request_requires_csrf_token(self):
        status, session = self.request_json("GET", "/api/session")
        self.assertEqual(status, 200)
        self.csrf = session["csrfToken"]
        status, result = self.request_json(
            "POST",
            "/api/auth/setup",
            {"username": "webtester", "password": "a-strong-test-password"},
            csrf=False,
        )
        self.assertEqual(status, 401)
        self.assertIn("session token", result["error"].lower())

    def test_server_refuses_non_local_bind_address(self):
        with self.assertRaises(ValueError):
            create_server(host="0.0.0.0", port=0)


    def test_login_rotates_session_and_csrf_token(self):
        self.sign_in_first_account()
        old_cookie = self.cookie
        old_csrf = self.csrf
        status, result = self.request_json("POST", "/api/auth/logout", {})
        self.assertEqual(status, 200, result)
        self.csrf = result["csrfToken"]
        status, result = self.request_json(
            "POST",
            "/api/auth/login",
            {"username": "webtester", "password": "a-strong-test-password"},
        )
        self.assertEqual(status, 200, result)
        self.assertNotEqual(self.cookie, old_cookie)
        self.assertNotEqual(result["csrfToken"], old_csrf)
        self.csrf = result["csrfToken"]

    def test_logout_does_not_read_ticket_storage(self):
        self.sign_in_first_account()
        Path(self.temp.name, "tickets.json").write_text("{broken", encoding="utf-8")
        status, result = self.request_json("POST", "/api/auth/logout", {})
        self.assertEqual(status, 200, result)
        self.assertTrue(result["ok"])

    def test_static_files_have_consistent_content_security_policy(self):
        for path in ("/", "/app.css", "/app.js"):
            self.connection.request("GET", path)
            response = self.connection.getresponse()
            response.read()
            self.assertEqual(response.status, 200)
            policy = response.getheader("Content-Security-Policy")
            self.assertIn("style-src 'self'", policy)
            self.assertNotIn("unsafe-inline", policy)
            self.assertIn("script-src 'self'", policy)

    def test_login_throttle_is_shared_between_sessions(self):
        self.sign_in_first_account()
        status, result = self.request_json("POST", "/api/auth/logout", {})
        self.assertEqual(status, 200, result)
        session_status, session = self.request_json("GET", "/api/session")
        self.assertEqual(session_status, 200)
        self.csrf = session["csrfToken"]
        for _ in range(5):
            status, _ = self.request_json(
                "POST",
                "/api/auth/login",
                {"username": "webtester", "password": "incorrect-password"},
            )
            self.assertEqual(status, 401)
        status, result = self.request_json(
            "POST",
            "/api/auth/login",
            {"username": "webtester", "password": "a-strong-test-password"},
        )
        self.assertEqual(status, 429)
        self.assertIn("15 minutes", result["error"])


    def test_ticket_assignment_status_notes_and_reopen(self):
        self.sign_in_first_account()
        status, created = self.request_json(
            "POST", "/api/tickets",
            {"title": "Lab computer issue", "category": "Hardware",
             "urgency": "medium", "affected_users": 3},
        )
        self.assertEqual(status, 200, created)
        ticket_id = created["ticket"]["id"]
        status, assigned = self.request_json(
            "POST", "/api/tickets/assign",
            {"ticket_id": ticket_id, "assignee": "Support Team"},
        )
        self.assertEqual(status, 200, assigned)
        status, changed = self.request_json(
            "POST", "/api/tickets/status",
            {"ticket_id": ticket_id, "status": "in_progress"},
        )
        self.assertEqual(status, 200, changed)
        status, noted = self.request_json(
            "POST", "/api/tickets/notes",
            {"ticket_id": ticket_id, "author": "webtester",
             "message": "Checked the affected workstation."},
        )
        self.assertEqual(status, 200, noted)
        self.assertEqual(noted["ticket"]["notes"][0]["note_id"], "N001")
        status, resolved = self.request_json(
            "POST", "/api/tickets/status",
            {"ticket_id": ticket_id, "status": "resolved"},
        )
        self.assertEqual(status, 200, resolved)
        status, reopened = self.request_json(
            "POST", "/api/tickets/reopen", {"ticket_id": ticket_id},
        )
        self.assertEqual(status, 200, reopened)
        self.assertEqual(reopened["ticket"]["status"], "open")

    def test_invalid_ticket_assignment_does_not_change_saved_data(self):
        self.sign_in_first_account()
        status, created = self.request_json(
            "POST", "/api/tickets",
            {"title": "Projector issue", "category": "Hardware",
             "urgency": "low", "affected_users": 1},
        )
        self.assertEqual(status, 200, created)
        status, result = self.request_json(
            "POST", "/api/tickets/assign",
            {"ticket_id": created["ticket"]["id"], "assignee": "   "},
        )
        self.assertEqual(status, 400)
        status, listed = self.request_json("GET", "/api/tickets")
        self.assertEqual(status, 200)
        self.assertIsNone(listed["tickets"][0]["assigned_to"])


if __name__ == "__main__":
    unittest.main()
