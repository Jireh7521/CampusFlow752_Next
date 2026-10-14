# CampusFlow

CampusFlow is a Python command-line helpdesk for Learn2Earn campus staff. It records technical
support requests (Wi-Fi outages, faulty laptops, broken dev environments), calculates their
priority, assigns them to staff, tracks progress, and saves everything to a JSON file.

## Team

| Fellow | Role | Contribution |
|--------|------|--------------|
| _Engineer A name_ | _e.g. tickets, validation, priority_ | _fill in_ |
| _Engineer B name_ | _e.g. workflow, queue, reports_ | _fill in_ |

## Requirements and setup

- Python 3.8 or newer. Standard library only; nothing to install.

```
git clone <repository-url>
cd <repository-folder>
python main.py
```

## Menu

| Option | What it does |
|--------|--------------|
| 1 | Create a ticket (title, category, urgency, affected users) |
| 2 | List all tickets |
| 3 | View one ticket in detail |
| 4 | Assign a ticket to a staff member |
| 5 | Change status (`in_progress`, `resolved`) |
| 6 | Reopen a resolved ticket |
| 7 | Show the work queue |
| 8 | Show the report |
| 9 | Add a follow-up note |
| 0 | Exit |

The menu runs until you choose Exit. Invalid input shows an `Error:` message and never changes
or corrupts stored tickets.

## Ticket fields and validation

Tickets contain `id`, `title`, `category`, `urgency`, `affected_users`, `priority`, `status`,
`assigned_to`, and `notes`.

- IDs are generated automatically: `T001`, `T002`, ...
- Categories: `Network`, `Hardware`, `Software`, `Other`. Urgency: `low`, `medium`, `high`.
  Any letter case is accepted during ticket creation and normalized.
- Title must not be blank. Affected users must be a whole number of 1 or more
  (0, negatives, decimals and text are rejected).
- Follow-up notes have a per-ticket ID (`N001`, `N002`, ...), a nonblank author, and a message
  containing 5–300 characters. Notes can be added to open or in-progress tickets.

## Priority rules

The first matching rule wins:

1. `high` urgency **and** 10+ affected users -> `critical`
2. `high` urgency **or** 10+ affected users -> `high`
3. `medium` urgency **or** 3+ affected users -> `medium`
4. everything else -> `low`

## Status workflow

```
open  ->  in_progress  ->  resolved
  ^                           |
  +-------- reopen -----------+
```

| From | Allowed next status |
|------|---------------------|
| `open` | `in_progress` |
| `in_progress` | `resolved` |
| `resolved` | `open` (reopen) |

- A ticket with no assignee cannot move to `in_progress`.
- Skipping a step or moving backwards is rejected.
- A resolved ticket cannot be modified (including assignment or notes) until it is reopened.

## Work queue

Shows `open` tickets ordered `critical` -> `high` -> `medium` -> `low`. Tickets with the same
priority are ordered by the earlier numeric ticket ID (`T2` before `T10`).
`in_progress` and `resolved` tickets are not listed.

## Reports

Total ticket count plus counts by status and by priority. Every category is shown, with 0
when unused, so an empty system still gives a valid report.

## JSON persistence and validation

Tickets are saved to `data/tickets.json` after every successful change and loaded on startup.
The supported format is a JSON **list of ticket objects**. Each ticket has the required fields
listed above; `notes` is a list of objects containing `note_id`, `author`, and `message`.

- **Missing file:** the app starts with no tickets.
- **Malformed JSON or invalid data:** startup is rejected with a clear error; the app does not
  replace the current collection with a partially decoded collection or overwrite the file.
- **Validation:** ticket IDs must be unique; required fields, category, urgency, positive
  affected-user count, calculated priority, status, assignee, and note structure are checked.
  Duplicate note IDs within one ticket are rejected.
- **Legacy compatibility:** valid ticket records written before follow-up notes were added may
  omit `notes`; they load with an empty list. Other missing required fields are not migrated.
- **ID continuity:** ticket and note IDs are generated from the highest existing numeric ID after
  reload, so adding records does not reuse an existing ID.
- **Saving:** a temporary file is written and then atomically moved into place. Invalid collections
  are rejected before the existing file is replaced.
- **Start fresh:** back up and then delete or move `data/tickets.json`.
- `data/tickets.json` is ignored by Git.

## Running the tests

```
python -m unittest discover -s tests -v
```

| File | Covers |
|------|--------|
| `tests/test_tickets.py` | priority rules and boundaries, validation, ID generation, assign, list/view |
| `tests/test_workflow.py` | transitions, unassigned rule, reopen, unknown IDs, no-change on failure |
| `tests/test_work_queue.py` | priority order, numeric tie-break, open-only filter |
| `tests/test_reports.py` | empty report, mixed counts, corrupt data |
| `tests/test_storage.py` | complete save/reload, legacy notes migration, malformed JSON, invalid fields, duplicate IDs, state preservation and ID continuity |
| `tests/test_notes.py` | note validation, lifecycle, display order, save/load continuity |
| `tests/test_cli.py` | scripted full menu sessions, restart, corrupted file at startup |

## Project layout

```
main.py                  entry point
campusflow/
  tickets.py             create, validation, priority, assign, list/view
  notes.py               follow-up notes
  workflow.py            status transitions, reopen
  work_queue.py          priority-sorted open queue
  reports.py             totals and breakdowns
  storage.py             JSON load/save and collection validation
  cli.py                 text menu
tests/                   unittest suites
docs/                    design-decisions.md, ai-learning-log.md
```

## Known limitations

- Text interface only; one user at a time (no file locking).
- The queue lists `open` tickets only; `in_progress` tickets are not shown in it.
- `in_progress -> open` is not supported; only resolved tickets can be reopened.
- Reopening keeps the previous assignee.
- Staff names are free text (no staff list).
- Tickets cannot be deleted or edited except for assignment, status and notes.

## Pull requests

- Engineer A PR: _link_
- Engineer B PR: _link_
