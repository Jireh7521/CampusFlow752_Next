# CampusFlow

CampusFlow is a Python command-line helpdesk for Learn2Earn campus staff. It records technical
support requests (Wi-Fi outages, faulty laptops, broken development environments), calculates
their priority, assigns them to staff, tracks progress, stores follow-up notes, supports searching,
and saves tickets to JSON.

It also includes an **Engineering Understanding Check**: a six-question multiple-choice quiz about
the project's engineering rules. It validates answers, retries invalid choices, calculates a score,
and asks the learner to explain two answers for mentor discussion.

## Team

| Fellow | Role | Contribution |
|--------|------|--------------|
| _Engineer A name_ | _Confirm actual role_ | _Record the tests and features actually contributed_ |
| _Engineer B name_ | _Confirm actual role_ | _Record the tests and features actually contributed_ |

Replace these placeholders with both engineers' agreed names, roles, and verified contributions.
Do not claim work or reviews that have not been completed.

## Requirements and setup

- Python 3.8 or newer.
- Standard library only; no third-party runtime dependencies.

```bash
git clone https://github.com/Jireh7521/CampusFlow752_Next.git
cd CampusFlow752_Next
python3 -m unittest discover -s tests -v
python3 main.py
```

## Authentication

CampusFlow requires a local username and password before displaying ticket information.

- On the first run, create the first account when prompted. Usernames are 3–32 characters and may contain letters, numbers, periods, underscores, and hyphens.
- Passwords must be at least 12 characters. Password input is hidden in a real terminal.
- On later runs, sign in with that account. Three failed attempts end the current run.
- Accounts are stored separately in `data/users.json`. Passwords are stored as salted PBKDF2-HMAC-SHA256 hashes (600,000 iterations), not plain text. On platforms that support POSIX permissions, the account file is restricted to its owner.
- Ticket data remains in `data/tickets.json`; account records and tickets are separate files.
- If the account file is malformed, CampusFlow stops instead of silently replacing it.

This is local CLI authentication, not a multi-user server or a complete operating-system security boundary. Anyone who can change the program or access the local account file may be able to tamper with the local installation. Use a unique password and protect access to the computer and project files.

## Menu

| Option | What it does |
|--------|--------------|
| 1 | Create a ticket |
| 2 | List all tickets |
| 3 | View one ticket |
| 4 | Assign a ticket |
| 5 | Change ticket status |
| 6 | Reopen a resolved ticket |
| 7 | Show the work queue |
| 8 | Show the report |
| 9 | Add a follow-up note |
| 10 | Search tickets with optional filters |
| 11 | Search tickets in priority order |
| 12 | Run the Engineering Understanding Check |
| 0 | Exit |

The menu repeats until you choose Exit. Invalid input displays an error or validation message.
A rejected action must not partially modify or overwrite saved ticket data.

## Tickets, validation, and IDs

Ticket fields include `id`, `title`, `category`, `urgency`, `affected_users`, `priority`,
`status`, `assigned_to`, and `notes`.

- IDs are generated automatically as `T001`, `T002`, and so on.
- Categories: `Network`, `Hardware`, `Software`, `Other`.
- Urgency: `low`, `medium`, `high`.
- Category and urgency accept letter-case variations and are normalized.
- Titles cannot be blank. Affected users must be a positive whole number; zero, negatives,
  decimals, booleans, and invalid text are rejected.

## Priority rules

The first matching rule wins:

1. `high` urgency **and** 10 or more affected users → `critical`
2. `high` urgency **or** 10 or more affected users → `high`
3. `medium` urgency **or** 3 or more affected users → `medium`
4. Otherwise → `low`

## Status workflow

```text
open -> in_progress -> resolved
 ^                       |
 +-------- reopen -------+
```

- A ticket must have an assignee before it can move to `in_progress`.
- Skipping a step or making an unsupported transition is rejected.
- A resolved ticket cannot be assigned or otherwise modified until reopened.
- Reopening changes the status to `open` and retains the previous assignee.

## Follow-up notes

Notes have sequential IDs such as `N001` and `N002`, and include an author and message.
Blank or invalid note fields are rejected. Notes cannot be added to a resolved ticket until it
has been reopened. Notes and note-ID continuity are preserved when tickets are saved and loaded.

## Work queue, search, and reports

- The work queue lists `open` tickets ordered `critical` → `high` → `medium` → `low`.
  Ties are sorted by the numeric portion of the ticket ID. Other statuses are excluded.
- Search supports a title query and optional category, status, and priority filters. Filters are
  combined, and a separate menu option sorts search results by priority.
- Reports show total ticket count; counts by every status, priority, and category (including zero-count values); unresolved and resolved totals; and the resolution percentage based on each ticket's current status. Empty reports show zero counts and a 0% resolution percentage.

## Engineering Understanding Check

Choose menu option **12** to run the six-question multiple-choice check. Questions cover engineering
decisions and rules in the project. Answers are case-insensitive; invalid choices are rejected and
the user is prompted again until a valid A/B/C/D answer is entered. The check awards one point per
correct answer and prints a score out of six. The learner must also provide two non-empty
explanations, which are displayed for mentor discussion.

The quiz logic and scoring are separated into testable functions. Automated tests cover the question
bank, full and zero scores, partial scoring, invalid choices, answer retry behavior, and displayed
results. The check is intended to support understanding, not replace code review or hands-on work.

## JSON persistence and safety

Tickets are saved to `data/tickets.json` after each successful change and loaded on startup.

- If the file is missing, CampusFlow starts with no tickets.
- Corrupt JSON, duplicate ticket IDs, or invalid persisted collections are rejected safely.
- CampusFlow refuses to start when stored data cannot be read safely; it does not silently replace
  the unreadable file.
- Ticket IDs continue from the highest existing ID after reload.
- Local data files are ignored by Git.

### Supported JSON format

The file is a JSON array (list) of ticket objects, not a wrapper object. Each ticket stores its
ID, title, canonical category and urgency, affected-user count, calculated priority, status,
assignee (`null` when unassigned), and a list of follow-up notes. Older tickets may omit `notes`;
loading them supplies an empty list in memory.

```json
[
  {
    "id": "T001",
    "title": "Campus Wi-Fi is down",
    "category": "Network",
    "urgency": "high",
    "affected_users": 15,
    "priority": "critical",
    "status": "open",
    "assigned_to": null,
    "notes": [
      {
        "note_id": "N001",
        "author": "Amina",
        "message": "Checked the router."
      }
    ]
  }
]
```

Ticket IDs must be unique strings in `T`-plus-digits form. Categories are `Network`, `Hardware`,
`Software`, or `Other`; urgency is `low`, `medium`, or `high`; status is `open`, `in_progress`, or
`resolved`. `affected_users` must be a positive integer (not a boolean or decimal), and `priority`
must match the priority rules above. Each note needs a unique per-ticket `note_id` in `N`-plus-digits
form, a nonblank author, and a 5–300 character message. Invalid or inconsistent records are rejected
rather than silently corrected.

## Running the tests

From the repository root, run:

```bash
python -m unittest discover -s tests -v
```

The test suite uses Python's built-in `unittest`; no extra test packages are required.

| Test file | Coverage |
|-----------|----------|
| `tests/test_auth.py` | Password hashing, login, validation, account persistence, malformed account data |
| `tests/test_tickets.py` | Priority rules, validation, IDs, assignment, ticket views, search |
| `tests/test_workflow.py` | Status transitions, unassigned-ticket rule, reopening, rejected changes |
| `tests/test_work_queue.py` | Priority ordering, numeric ID tie-breaks, included statuses |
| `tests/test_reports.py` | Empty reports, status/priority counts, report changes |
| `tests/test_storage.py` | Save/load, missing and corrupt files, collection validation, ID continuity |
| `tests/test_notes.py` | Note validation, sequential IDs, workflow restrictions, persistence |
| `tests/test_cli.py` | First-run account setup, login failures, menu sessions, restart behavior, safe error handling |
| `tests/test_engineering_check.py` | Question bank, scoring, invalid-answer retries, quiz output |

## Final demonstration

Use [`docs/final-demo-checklist.md`](docs/final-demo-checklist.md) to record the fresh-clone test result, manual workflow/search/report/persistence checks, review evidence, and any remaining defects. It is a checklist only; record actual observations during the demonstration rather than treating expected behavior as a test result.

## Project layout

```text
main.py
campusflow/
  auth.py                       local account creation and password verification
  tickets.py                    ticket creation, validation, priority, search
  workflow.py                   status transitions and reopening
  work_queue.py                 priority-sorted work queue
  reports.py                    totals and breakdowns
  storage.py                    ticket JSON load/save and validation
  notes.py                      follow-up notes
  engineering_check.py          quiz interaction and scoring
  engineering_check_questions.py question bank
  cli.py                        authentication and text menu
tests/                           unittest suites
docs/                            design decisions and learning log
```

## Known limitations

- Text interface only; designed for one local user at a time.
- The work queue lists `open` tickets only; `in_progress` tickets are not shown.
- Moving directly from `in_progress` back to `open` is unsupported; only resolved tickets can be reopened.
- Staff names are free text; there is no staff directory or role-based permissions.
- Authentication protects the normal CLI flow but does not encrypt ticket data or protect against someone with direct access to the local files.
- Tickets cannot be deleted or freely edited.

## Pull requests

- Engineer A PR: _add the actual PR link_
- Engineer B PR: _add the actual PR link_
