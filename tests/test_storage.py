import copy
import json
import os
import tempfile
import unittest

from campusflow.notes import add_note
from campusflow.storage import StorageError, load_tickets, save_tickets
from campusflow.tickets import create_ticket


def make_tickets():
    tickets = []
    create_ticket(tickets, "Wi-Fi down", "Network", "high", 15)
    create_ticket(tickets, "Broken laptop", "Hardware", "low", 1)
    tickets[1]["assigned_to"] = "Amina"
    add_note(tickets, "T001", "Amina", "Router checked.")
    return tickets


class TestStorage(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.addCleanup(self.folder.cleanup)
        self.path = os.path.join(self.folder.name, "data", "tickets.json")

    def write_json(self, data):
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as handle:
            json.dump(data, handle)

    def test_missing_file_gives_fresh_start(self):
        self.assertEqual(load_tickets(self.path), [])

    def test_save_and_reload_preserves_every_ticket_and_note_field(self):
        tickets = make_tickets()
        save_tickets(tickets, self.path)
        self.assertEqual(load_tickets(self.path), tickets)

    def test_save_creates_missing_folder(self):
        save_tickets([], self.path)
        self.assertTrue(os.path.exists(self.path))

    def test_new_ticket_and_note_after_reload_keep_ids_unique(self):
        tickets = make_tickets()
        save_tickets(tickets, self.path)
        reloaded = load_tickets(self.path)

        new_ticket = create_ticket(reloaded, "New issue", "Other", "low", 1)
        new_note = add_note(reloaded, "T001", "Bola", "Second update.")

        self.assertEqual(new_ticket["id"], "T003")
        self.assertEqual(new_note["notes"][-1]["note_id"], "N002")
        ticket_ids = [ticket["id"] for ticket in reloaded]
        note_ids = [note["note_id"] for note in reloaded[0]["notes"]]
        self.assertEqual(len(ticket_ids), len(set(ticket_ids)))
        self.assertEqual(len(note_ids), len(set(note_ids)))

    def test_corrupted_json_raises_clear_error_and_keeps_file(self):
        os.makedirs(os.path.dirname(self.path))
        invalid_json = '[{"id": "T001", '
        with open(self.path, "w", encoding="utf-8") as handle:
            handle.write(invalid_json)

        with self.assertRaises(StorageError) as context:
            load_tickets(self.path)

        self.assertIn("not valid JSON", str(context.exception))
        with open(self.path, encoding="utf-8") as handle:
            self.assertEqual(handle.read(), invalid_json)

    def test_wrong_collection_or_ticket_shape_is_rejected(self):
        for content in ('{"id": "T001"}', '[1, 2]', '[{"id": "T001"}]'):
            with self.subTest(content=content):
                with open(self.path, "w", encoding="utf-8") as handle:
                    handle.write(content)
                with self.assertRaises(StorageError):
                    load_tickets(self.path)

    def test_duplicate_ticket_ids_are_rejected_including_numeric_aliases(self):
        tickets = make_tickets()
        tickets[1]["id"] = tickets[0]["id"]
        self.write_json(tickets)
        with self.assertRaises(StorageError):
            load_tickets(self.path)

        tickets[1]["id"] = "T1"
        self.write_json(tickets)
        with self.assertRaises(StorageError):
            load_tickets(self.path)

    def test_invalid_fields_and_inconsistent_priority_are_rejected(self):
        invalid_updates = [
            {"title": "   "},
            {"category": "Plumbing"},
            {"urgency": "urgent"},
            {"affected_users": True},
            {"affected_users": 0},
            {"priority": "low"},
            {"status": "waiting"},
            {"assigned_to": ""},
        ]
        for update in invalid_updates:
            with self.subTest(update=update):
                tickets = make_tickets()
                tickets[0].update(update)
                self.write_json(tickets)
                with self.assertRaises(StorageError):
                    load_tickets(self.path)

    def test_malformed_notes_and_duplicate_note_ids_are_rejected(self):
        invalid_notes = [
            [{"note_id": "N001", "author": "Amina"}],
            [{"note_id": "N001", "author": "Amina", "message": "tiny"}],
            [
                {"note_id": "N001", "author": "Amina", "message": "First update"},
                {"note_id": "N001", "author": "Bola", "message": "Second update"},
            ],
            [
                {"note_id": "N1", "author": "Amina", "message": "First update"},
                {"note_id": "N001", "author": "Bola", "message": "Second update"},
            ],
        ]
        for notes in invalid_notes:
            with self.subTest(notes=notes):
                tickets = make_tickets()
                tickets[0]["notes"] = notes
                self.write_json(tickets)
                with self.assertRaises(StorageError):
                    load_tickets(self.path)

    def test_legacy_tickets_without_notes_migrate_without_mutating_input(self):
        tickets = make_tickets()
        del tickets[0]["notes"]
        original = copy.deepcopy(tickets)
        save_tickets(tickets, self.path)
        loaded = load_tickets(self.path)

        self.assertEqual(tickets, original)
        self.assertEqual(loaded[0]["notes"], [])

    def test_invalid_collection_does_not_mutate_input_or_overwrite_saved_data(self):
        valid = make_tickets()
        save_tickets(valid, self.path)
        with open(self.path, encoding="utf-8") as handle:
            saved_before = handle.read()

        invalid = make_tickets()
        invalid[0]["priority"] = "low"
        original = copy.deepcopy(invalid)
        with self.assertRaises(StorageError):
            save_tickets(invalid, self.path)

        self.assertEqual(invalid, original)
        with open(self.path, encoding="utf-8") as handle:
            self.assertEqual(handle.read(), saved_before)

    def test_save_leaves_no_temp_file(self):
        save_tickets(make_tickets(), self.path)
        self.assertFalse(os.path.exists(self.path + ".tmp"))


if __name__ == "__main__":
    unittest.main()
