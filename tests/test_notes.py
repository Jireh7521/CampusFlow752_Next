import copy
import json
import os
import tempfile
import unittest

from campusflow.notes import add_note
from campusflow.storage import load_tickets, save_tickets
from campusflow.tickets import create_ticket, format_ticket


def make_ticket(status="open"):
    tickets = []
    create_ticket(tickets, "Wi-Fi issue", "Network", "high", 5)
    tickets[0]["status"] = status
    return tickets


class TestFollowUpNotes(unittest.TestCase):
    def test_multiple_notes_receive_sequential_ids_and_are_displayed_in_order(self):
        tickets = make_ticket()
        add_note(tickets, "T001", "Amina", "Checked the router.")
        add_note(tickets, "T001", "Bola", "Waiting for replacement.")
        self.assertEqual(
            [note["note_id"] for note in tickets[0]["notes"]], ["N001", "N002"]
        )
        rendered = format_ticket(tickets[0])
        self.assertLess(rendered.index("N001"), rendered.index("N002"))

    def test_author_and_message_are_trimmed(self):
        tickets = make_ticket()
        add_note(tickets, "T001", "  Amina  ", "  Router checked  ")
        self.assertEqual(
            tickets[0]["notes"][0],
            {"note_id": "N001", "author": "Amina", "message": "Router checked"},
        )

    def test_invalid_notes_do_not_consume_ids_or_mutate_ticket(self):
        tickets = make_ticket()
        before = copy.deepcopy(tickets)
        for author, message in [
            (" ", "Valid message"),
            ("Amina", "four"),
            ("Amina", "x" * 301),
            (None, "Valid message"),
            ("Amina", None),
        ]:
            with self.subTest(author=author, message=message):
                with self.assertRaises(ValueError):
                    add_note(tickets, "T001", author, message)
                self.assertEqual(tickets, before)
        add_note(tickets, "T001", "Amina", "Valid message")
        self.assertEqual(tickets[0]["notes"][0]["note_id"], "N001")

    def test_message_boundaries_five_and_three_hundred_characters(self):
        tickets = make_ticket()
        add_note(tickets, "T001", "Amina", "12345")
        add_note(tickets, "T001", "Amina", "x" * 300)
        self.assertEqual(len(tickets[0]["notes"]), 2)

    def test_resolved_rejects_notes_but_reopened_ticket_accepts_them(self):
        tickets = make_ticket(status="resolved")
        before = copy.deepcopy(tickets)
        with self.assertRaises(ValueError):
            add_note(tickets, "T001", "Amina", "Valid message")
        self.assertEqual(tickets, before)
        tickets[0]["status"] = "open"
        add_note(tickets, "T001", "Amina", "After reopening")
        self.assertEqual(tickets[0]["notes"][0]["note_id"], "N001")

    def test_notes_and_note_id_continuity_survive_save_and_load(self):
        tickets = make_ticket()
        add_note(tickets, "T001", "Amina", "First update")
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "tickets.json")
            save_tickets(tickets, path)
            loaded = load_tickets(path)
            add_note(loaded, "T001", "Bola", "Second update")
        self.assertEqual(
            [note["note_id"] for note in loaded[0]["notes"]], ["N001", "N002"]
        )

    def test_legacy_ticket_without_notes_loads_with_empty_notes(self):
        tickets = make_ticket()
        del tickets[0]["notes"]
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "tickets.json")
            with open(path, "w", encoding="utf-8") as handle:
                json.dump(tickets, handle)
            loaded = load_tickets(path)
        self.assertEqual(loaded[0]["notes"], [])


if __name__ == "__main__":
    unittest.main()
