import copy
import json
import os
import tempfile
import unittest

from campusflow.storage import StorageError, _check_shape, load_tickets, save_tickets
from campusflow.tickets import create_ticket


def make_tickets():
    tickets = []
    create_ticket(tickets, "Wi-Fi down", "Network", "high", 15)
    create_ticket(tickets, "Broken laptop", "Hardware", "low", 1)
    tickets[1]["assigned_to"] = "Amina"
    return tickets


class TestStorage(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.path = os.path.join(self.folder.name, "data", "tickets.json")

    def test_missing_file_gives_fresh_start(self):
        self.assertEqual(load_tickets(self.path), [])

    def test_save_and_reload_preserves_tickets(self):
        tickets = make_tickets()
        save_tickets(tickets, self.path)
        self.assertEqual(load_tickets(self.path), tickets)

    def test_save_creates_missing_folder(self):
        save_tickets([], self.path)
        self.assertTrue(os.path.exists(self.path))

    def test_new_ticket_after_reload_does_not_duplicate_ids(self):
        save_tickets(make_tickets(), self.path)
        reloaded = load_tickets(self.path)
        new = create_ticket(reloaded, "New issue", "Other", "low", 1)
        self.assertEqual(new["id"], "T003")
        ids = [t["id"] for t in reloaded]
        self.assertEqual(len(ids), len(set(ids)))

    def test_corrupted_json_raises_clear_error_and_keeps_file(self):
        os.makedirs(os.path.dirname(self.path))
        broken_json = '[{"id": "T001", '
        with open(self.path, "w", encoding="utf-8") as handle:
            handle.write(broken_json)
        with self.assertRaises(StorageError) as context:
            load_tickets(self.path)
        self.assertIn("not valid JSON", str(context.exception))
        with open(self.path, encoding="utf-8") as handle:
            self.assertEqual(handle.read(), broken_json)

    def test_invalid_utf8_file_raises_storage_error_and_is_preserved(self):
        invalid_bytes = b"\xff\xfe"
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "wb") as handle:
            handle.write(invalid_bytes)

        with self.assertRaises(StorageError):
            load_tickets(self.path)

        with open(self.path, "rb") as handle:
            self.assertEqual(handle.read(), invalid_bytes)

    def test_wrong_shape_rejected(self):
        os.makedirs(os.path.dirname(self.path))
        for content in ('{"id": "T001"}', '[1, 2]', '[{"id": "T001"}]'):
            with self.subTest(content=content):
                with open(self.path, "w", encoding="utf-8") as handle:
                    handle.write(content)
                with self.assertRaises(StorageError):
                    load_tickets(self.path)

    def test_duplicate_ids_in_file_rejected(self):
        tickets = make_tickets()
        tickets[1]["id"] = tickets[0]["id"]
        os.makedirs(os.path.dirname(self.path))
        with open(self.path, "w", encoding="utf-8") as handle:
            json.dump(tickets, handle)
        with self.assertRaises(StorageError):
            load_tickets(self.path)

    def test_invalid_persisted_ticket_fields_are_rejected(self):
        invalid_cases = [
            ("title", ""),
            ("category", "Plumbing"),
            ("urgency", "urgent"),
            ("affected_users", 0),
            ("affected_users", -1),
            ("affected_users", 2.5),
            ("affected_users", True),
            ("status", "closed"),
            ("assigned_to", 42),
            ("assigned_to", "   "),
        ]
        for field, value in invalid_cases:
            with self.subTest(field=field, value=value):
                tickets = make_tickets()
                tickets[0][field] = value
                os.makedirs(os.path.dirname(self.path), exist_ok=True)
                with open(self.path, "w", encoding="utf-8") as handle:
                    json.dump(tickets, handle)
                with self.assertRaises(StorageError):
                    load_tickets(self.path)

    def test_priority_inconsistent_with_urgency_and_affected_users_is_rejected(self):
        tickets = make_tickets()
        tickets[0]["priority"] = "low"
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as handle:
            json.dump(tickets, handle)
        with self.assertRaisesRegex(StorageError, "does not match"):
            load_tickets(self.path)

    def test_invalid_collection_does_not_modify_source_file(self):
        tickets = make_tickets()
        tickets[0]["affected_users"] = False
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as handle:
            json.dump(tickets, handle)
        with open(self.path, encoding="utf-8") as handle:
            original = handle.read()

        with self.assertRaises(StorageError):
            load_tickets(self.path)

        with open(self.path, encoding="utf-8") as handle:
            self.assertEqual(handle.read(), original)


    def test_failed_collection_validation_does_not_partially_mutate_input(self):
        tickets = make_tickets()
        tickets[0].pop("notes", None)  # legacy record requiring in-memory migration
        tickets[1]["status"] = "invalid"
        original = copy.deepcopy(tickets)

        with self.assertRaises(StorageError):
            _check_shape(tickets, self.path)

        self.assertEqual(tickets, original)
        self.assertNotIn("notes", tickets[0])

    def test_save_leaves_no_temp_file(self):
        save_tickets(make_tickets(), self.path)
        self.assertFalse(os.path.exists(self.path + ".tmp"))


if __name__ == "__main__":
    unittest.main()
