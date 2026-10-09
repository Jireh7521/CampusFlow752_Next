import json
import os
import tempfile
import unittest

from campusflow.storage import StorageError, load_tickets, save_tickets
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
        with open(self.path, "w") as handle:
            handle.write('[{"id": "T001", ')
        with self.assertRaises(StorageError) as context:
            load_tickets(self.path)
        self.assertIn("not valid JSON", str(context.exception))
        with open(self.path) as handle:
            self.assertEqual(handle.read(), '[{"id": "T001", ')

    def test_wrong_shape_rejected(self):
        os.makedirs(os.path.dirname(self.path))
        for content in ('{"id": "T001"}', '[1, 2]', '[{"id": "T001"}]'):
            with self.subTest(content=content):
                with open(self.path, "w") as handle:
                    handle.write(content)
                with self.assertRaises(StorageError):
                    load_tickets(self.path)

    def test_duplicate_ids_in_file_rejected(self):
        tickets = make_tickets()
        tickets[1]["id"] = tickets[0]["id"]
        os.makedirs(os.path.dirname(self.path))
        with open(self.path, "w") as handle:
            json.dump(tickets, handle)
        with self.assertRaises(StorageError):
            load_tickets(self.path)

    def test_save_leaves_no_temp_file(self):
        save_tickets(make_tickets(), self.path)
        self.assertFalse(os.path.exists(self.path + ".tmp"))


if __name__ == "__main__":
    unittest.main()
