"""Scenario-based questions about CampusFlow's safety and behavior.

Keep this question bank independent of CLI prompting and scoring.
Each item has a prompt, four options, and the correct option letter.
"""

QUESTION_BANK = (
    {
        "question": "The tickets JSON file contains malformed JSON. What should CampusFlow do at startup?",
        "options": {
            "A": "Treat the file as empty and overwrite it on the next save.",
            "B": "Stop startup with a clear error and leave the file unchanged.",
            "C": "Delete the file automatically and create a new one.",
            "D": "Load only the first valid ticket and ignore the rest.",
        },
        "answer": "B",
    },
    {
        "question": "A ticket is open but unassigned. What happens if someone moves it to in_progress?",
        "options": {
            "A": "It succeeds because open tickets can always change status.",
            "B": "The ticket is silently assigned to the current user.",
            "C": "The transition is rejected until the ticket is assigned.",
            "D": "The ticket is automatically marked resolved.",
        },
        "answer": "C",
    },
    {
        "question": "A resolved ticket needs its assignee changed. What is the safe workflow?",
        "options": {
            "A": "Reopen it first, then change the assignee.",
            "B": "Edit assigned_to directly and leave it resolved.",
            "C": "Change its status to in_progress in one step.",
            "D": "Delete and recreate the ticket with the same ID.",
        },
        "answer": "A",
    },
    {
        "question": "A high-urgency ticket affects 12 users. Which priority should the priority engine assign?",
        "options": {
            "A": "Low, because the number of users is not relevant.",
            "B": "Medium, because only urgency determines priority.",
            "C": "High, because either high urgency or many users means high.",
            "D": "Critical, because high urgency and at least 10 affected users meet the first rule.",
        },
        "answer": "D",
    },
    {
        "question": "A user searches tickets by title and selects a category and status. How are these filters combined?",
        "options": {
            "A": "Only the title query is applied; other filters are ignored.",
            "B": "All supplied filters are combined with AND, and the search does not mutate tickets.",
            "C": "Filters are combined with OR, so any one match is enough.",
            "D": "Matching tickets are permanently sorted and saved.",
        },
        "answer": "B",
    },
    {
        "question": "Why does saving tickets write to a temporary file before replacing the data file?",
        "options": {
            "A": "To ensure a failed or interrupted write is less likely to leave a half-written tickets file.",
            "B": "To keep a permanent duplicate of every ticket.",
            "C": "To avoid validating the ticket data.",
            "D": "To make every save append duplicate tickets.",
        },
        "answer": "A",
    },
)
