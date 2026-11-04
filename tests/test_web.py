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


if __name__ == "__main__":
    unittest.main()
