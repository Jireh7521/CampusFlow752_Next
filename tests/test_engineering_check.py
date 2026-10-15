"""Tests for independently testable Engineering Understanding Check logic."""

import unittest

from campusflow.engineering_check import calculate_score, run_engineering_check
from campusflow.engineering_check_questions import QUESTION_BANK


class TestEngineeringCheckScoring(unittest.TestCase):
    def test_question_bank_contains_six_scenarios_with_four_options(self):
        self.assertEqual(len(QUESTION_BANK), 6)
        for question in QUESTION_BANK:
            self.assertEqual(set(question["options"]), {"A", "B", "C", "D"})
            self.assertIn(question["answer"], {"A", "B", "C", "D"})

    def test_all_correct_answers_score_six(self):
        answers = [question["answer"] for question in QUESTION_BANK]
        self.assertEqual(calculate_score(answers), 6)

    def test_all_wrong_answers_score_zero(self):
        answers = [
            next(letter for letter in "ABCD" if letter != question["answer"])
            for question in QUESTION_BANK
        ]
        self.assertEqual(calculate_score(answers), 0)

    def test_score_counts_only_correct_submitted_choices(self):
        answers = [question["answer"] for question in QUESTION_BANK[:3]]
        self.assertEqual(calculate_score(answers), 3)

    def test_invalid_choices_do_not_earn_points(self):
        answers = ["?", "A", "B", "C", "D", "X"]
        expected = sum(
            answer == question["answer"]
            for question, answer in zip(QUESTION_BANK, answers)
            if answer in {"A", "B", "C", "D"}
        )
        self.assertEqual(calculate_score(answers), expected)

    def test_cli_retries_invalid_choice_and_shows_score_and_explanations(self):
        answers = iter([
            "not valid",
            *[question["answer"].lower() for question in QUESTION_BANK],
            "The storage loader raises StorageError and does not save corrupted data.",
            "change_status checks the assignee before setting in_progress.",
        ])
        output = []

        def fake_input(_prompt=""):
            return next(answers)

        score = run_engineering_check(input_fn=fake_input, print_fn=output.append)
        rendered = "\n".join(output)
        self.assertEqual(score, 6)
        self.assertIn("Invalid answer", rendered)
        self.assertIn("Final score: 6/6", rendered)
        self.assertIn("Question 1: The storage loader", rendered)
        self.assertIn("Question 2: change_status", rendered)

    def test_blank_explanations_are_reprompted_and_trimmed(self):
        answers = iter([
            *[question["answer"] for question in QUESTION_BANK],
            "   ",
            "  StorageError protects the JSON file.  ",
            "",
            "  Status rules reject unassigned tickets.  ",
        ])
        output = []

        def fake_input(_prompt=""):
            return next(answers)

        score = run_engineering_check(input_fn=fake_input, print_fn=output.append)
        rendered = "\n".join(output)

        self.assertEqual(score, 6)
        self.assertEqual(rendered.count("Please enter an explanation"), 2)
        self.assertIn("Question 1: StorageError protects the JSON file.", rendered)
        self.assertIn("Question 2: Status rules reject unassigned tickets.", rendered)
        self.assertNotIn("Question 1:    ", rendered)


if __name__ == "__main__":
    unittest.main()
