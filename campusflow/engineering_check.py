"""Interaction and scoring for the Engineering Understanding Check."""

from campusflow.engineering_check_questions import QUESTION_BANK

VALID_ANSWERS = frozenset({"A", "B", "C", "D"})


def calculate_score(answers, questions=QUESTION_BANK):
    """Return one point per correct answer, capped at the six-question bank.

    Answers are positional: each submitted choice corresponds to the question
    at the same index. Invalid choices receive no point. This pure function
    can be tested without running the CLI.
    """
    score = 0
    for question, answer in zip(questions, answers):
        if isinstance(answer, str) and answer.strip().upper() in VALID_ANSWERS:
            if answer.strip().upper() == question["answer"]:
                score += 1
    return score


def _ask_answer(question, number, input_fn, print_fn):
    """Prompt until the learner submits exactly one valid A/B/C/D choice."""
    while True:
        answer = input_fn("Your answer (A/B/C/D): ").strip().upper()
        if answer in VALID_ANSWERS:
            return answer
        print_fn("Invalid answer. Please enter A, B, C, or D.")


def run_engineering_check(input_fn=input, print_fn=print):
    """Run all six questions, show the score, and capture two explanations."""
    print_fn("\n=== Engineering Understanding Check ===")
    print_fn("Answer each scenario by entering A, B, C, or D.")
    submitted_answers = []

    for index, item in enumerate(QUESTION_BANK, start=1):
        print_fn(f"\nQuestion {index} of {len(QUESTION_BANK)}: {item['question']}")
        for letter, option in item["options"].items():
            print_fn(f"  {letter}. {option}")
        submitted_answers.append(_ask_answer(item, index, input_fn, print_fn))

    score = calculate_score(submitted_answers)
    print_fn(f"\nFinal score: {score}/{len(QUESTION_BANK)}")

    explanations = []
    print_fn("Explain at least two answers using examples from the code.")
    for number in (1, 2):
        while True:
            explanation = input_fn(
                f"Explain your answer to question {number} (use a code example): "
            ).strip()
            if explanation:
                explanations.append((number, explanation))
                break
            print_fn("Please enter an explanation; it will be discussed with your mentor.")

    print_fn("\nExplanations for mentor discussion:")
    for number, explanation in explanations:
        print_fn(f"Question {number}: {explanation}")
    return score
