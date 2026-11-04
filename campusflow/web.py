"""Local web interface for CampusFlow.

Run with: python3 -m campusflow.web
The development server binds to 127.0.0.1 and is not intended for direct
public-internet deployment.
"""
import json
import mimetypes
import os
import secrets
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from campusflow.auth import (
    AuthenticationError, authenticate, create_user, load_users, save_users,
)
from campusflow.notes import add_note
from campusflow.reports import build_report
from campusflow.storage import (
    DEFAULT_PATH, StorageError, load_tickets, save_tickets,
)
from campusflow.tickets import (
    CATEGORIES, URGENCIES, assign_ticket, create_ticket,
    search_tickets, sort_tickets_by_priority,
)
from campusflow.workflow import change_status, reopen_ticket

WEB_DIR = Path(__file__).resolve().parent.parent / "web"
DEFAULT_USERS_PATH = os.path.join("data", "users.json")


class CampusFlowHandler(BaseHTTPRequestHandler):
    server_version = "CampusFlowWeb/1.0"

    def log_message(self, fmt, *args):
        # Keep logs useful without recording request bodies or credentials.
        super().log_message(fmt, *args)

    def _send_json(self, status, payload, headers=None):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'self'; style-src 'self'; script-src 'self'; connect-src 'self'; img-src 'self' data:; base-uri 'none'; frame-ancestors 'none'")
        if headers:
            for key, value in headers.items():
                self.send_header(key, value)
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, path):
        try:
            content = path.read_bytes()
        except FileNotFoundError:
            self._send_json(HTTPStatus.NOT_FOUND, {"error": "Page not found."})
            return
        content_type = mimetypes.guess_type(str(path))[0] or "application/octet-stream"
        if path.suffix == ".js":
            content_type = "text/javascript"
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", content_type + ("; charset=utf-8" if content_type.startswith("text/") or "javascript" in content_type else ""))
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-cache")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'self'; style-src 'self'; script-src 'self'; connect-src 'self'; img-src 'self' data:; base-uri 'none'; frame-ancestors 'none'")
        self.end_headers()
        self.wfile.write(content)

    def _body(self):
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            raise ValueError("Invalid request length.") from None
        if length < 0 or length > 64 * 1024:
            raise ValueError("Request body is too large.")
        raw = self.rfile.read(length)
        try:
            value = json.loads(raw or b"{}")
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise ValueError("Request body must be valid JSON.") from None
        if not isinstance(value, dict):
            raise ValueError("Request body must be a JSON object.")
        return value

    def _session(self):
        cookies = self.headers.get("Cookie", "")
        session_id = None
        for part in cookies.split(";"):
            key, separator, value = part.strip().partition("=")
            if separator and key == "campusflow_session":
                session_id = value
                break
        session = self.server.sessions.get(session_id) if session_id else None
        headers = {}
        if session is None:
            session_id = secrets.token_urlsafe(32)
            session = {"csrf": secrets.token_urlsafe(32), "username": None, "failed": 0}
            self.server.sessions[session_id] = session
            headers["Set-Cookie"] = (
                f"campusflow_session={session_id}; Path=/; HttpOnly; SameSite=Strict"
            )
        return session, headers

    def _require_csrf(self, session):
        supplied = self.headers.get("X-CSRF-Token", "")
        if not supplied or not secrets.compare_digest(supplied, session["csrf"]):
            raise PermissionError("Your session token is missing or expired. Refresh the page.")

    def _require_login(self, session):
        if not session.get("username"):
            raise PermissionError("Please sign in to continue.")

    def _tickets(self):
        try:
            return load_tickets(self.server.tickets_path)
        except StorageError:
            raise

    def _save_candidate(self, tickets):
        # Persist a candidate before returning it as the new in-memory state.
        save_tickets(tickets, self.server.tickets_path)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/":
            return self._send_file(WEB_DIR / "index.html")
        if parsed.path in ("/app.css", "/app.js"):
            return self._send_file(WEB_DIR / parsed.path.lstrip("/"))

        if not parsed.path.startswith("/api/"):
            return self._send_json(HTTPStatus.NOT_FOUND, {"error": "Not found."})

        session, headers = self._session()
        try:
            if parsed.path == "/api/session":
                users = load_users(self.server.users_path)
                return self._send_json(HTTPStatus.OK, {
                    "csrfToken": session["csrf"],
                    "setupRequired": len(users) == 0,
                    "authenticated": bool(session.get("username")),
                    "username": session.get("username"),
                }, headers)
            self._require_login(session)
            tickets = self._tickets()
            if parsed.path == "/api/tickets":
                return self._send_json(HTTPStatus.OK, {"tickets": tickets}, headers)
            if parsed.path == "/api/work-queue":
                from campusflow.work_queue import get_work_queue
                return self._send_json(HTTPStatus.OK, {"tickets": get_work_queue(tickets)}, headers)
            if parsed.path == "/api/reports":
                return self._send_json(HTTPStatus.OK, build_report(tickets), headers)
            return self._send_json(HTTPStatus.NOT_FOUND, {"error": "API route not found."}, headers)
        except PermissionError as error:
            return self._send_json(HTTPStatus.UNAUTHORIZED, {"error": str(error)}, headers)
        except (AuthenticationError, StorageError, OSError, ValueError) as error:
            return self._send_json(HTTPStatus.INTERNAL_SERVER_ERROR, {"error": str(error)}, headers)

    def do_POST(self):
        parsed = urlparse(self.path)
        if not parsed.path.startswith("/api/"):
            return self._send_json(HTTPStatus.NOT_FOUND, {"error": "Not found."})
        session, headers = self._session()
        try:
            self._require_csrf(session)
            data = self._body()

            if parsed.path in ("/api/auth/setup", "/api/auth/login"):
                users = load_users(self.server.users_path)
                if parsed.path.endswith("/setup"):
                    if users:
                        return self._send_json(HTTPStatus.CONFLICT, {"error": "An account already exists. Please sign in."}, headers)
                    create_user(users, data.get("username"), data.get("password"))
                    save_users(users, self.server.users_path)
                    session["username"] = users[-1]["username"]
                    session["failed"] = 0
                else:
                    if session["failed"] >= 3:
                        return self._send_json(HTTPStatus.TOO_MANY_REQUESTS, {"error": "Too many failed attempts. Refresh and try again later."}, headers)
                    try:
                        session["username"] = authenticate(users, data.get("username"), data.get("password"))
                        session["failed"] = 0
                    except ValueError:
                        session["failed"] += 1
                        return self._send_json(HTTPStatus.UNAUTHORIZED, {"error": "Invalid username or password."}, headers)
                return self._send_json(HTTPStatus.OK, {"username": session["username"]}, headers)

            self._require_login(session)
            tickets = self._tickets()
            candidate = json.loads(json.dumps(tickets))
            if parsed.path == "/api/auth/logout":
                session["username"] = None
                session["failed"] = 0
                return self._send_json(HTTPStatus.OK, {"ok": True}, headers)
            if parsed.path == "/api/tickets":
                ticket = create_ticket(
                    candidate, data.get("title"), data.get("category"),
                    data.get("urgency"), data.get("affected_users"),
                )
                result = {"ticket": ticket}
            elif parsed.path == "/api/tickets/assign":
                ticket = assign_ticket(candidate, data.get("ticket_id"), data.get("assignee"))
                result = {"ticket": ticket}
            elif parsed.path == "/api/tickets/status":
                ticket = change_status(candidate, data.get("ticket_id"), data.get("status"))
                result = {"ticket": ticket}
            elif parsed.path == "/api/tickets/reopen":
                ticket = reopen_ticket(candidate, data.get("ticket_id"))
                result = {"ticket": ticket}
            elif parsed.path == "/api/tickets/notes":
                ticket = add_note(candidate, data.get("ticket_id"), data.get("author"), data.get("message"))
                result = {"ticket": ticket}
            else:
                return self._send_json(HTTPStatus.NOT_FOUND, {"error": "API route not found."}, headers)
            self._save_candidate(candidate)
            return self._send_json(HTTPStatus.OK, result, headers)
        except PermissionError as error:
            return self._send_json(HTTPStatus.UNAUTHORIZED, {"error": str(error)}, headers)
        except (AuthenticationError, StorageError, OSError, ValueError) as error:
            status = HTTPStatus.BAD_REQUEST if isinstance(error, ValueError) and not isinstance(error, (StorageError, AuthenticationError)) else HTTPStatus.INTERNAL_SERVER_ERROR
            return self._send_json(status, {"error": str(error)}, headers)


def create_server(host="127.0.0.1", port=8000, tickets_path=DEFAULT_PATH, users_path=DEFAULT_USERS_PATH):
    """Create a local-only web server with injectable data paths for tests."""
    if host not in ("127.0.0.1", "localhost", "::1"):
        raise ValueError("CampusFlow's built-in web server must bind to localhost.")
    server = ThreadingHTTPServer((host, port), CampusFlowHandler)
    server.tickets_path = tickets_path
    server.users_path = users_path
    server.sessions = {}
    return server


def main():
    server = create_server()
    print(f"CampusFlow web interface: http://{server.server_address[0]}:{server.server_address[1]}")
    print("Local development server only. Do not expose this server to the public internet.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping CampusFlow web server.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
