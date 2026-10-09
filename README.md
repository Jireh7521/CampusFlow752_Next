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
| 0 | Exit |

The menu runs until you choose Exit. Invalid input shows an `Error:` message and never changes
or corrupts stored tickets.

## Ticket fields and validation

`id`, `title`, `category`, `urgency`, `affected_users`, `priority`, `status`, `assigned_to`.

- IDs are generated automatically: `T001`, `T002`, ...
- Categories: `Network`, `Hardware`, `Software`, `Other`. Urgency: `low`, `medium`, `high`.
  Any letter case is accepted and normalized.
- Title must not be blank. Affected users must be a whole number of 1 or more
  (0, negatives, decimals and text are rejected).

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

| From          | Allowed next status |
|---------------|---------------------|
| `open`        | `in_progress`       |
| `in_progress` | `resolved`          |
| `resolved`    | `open` (reopen)     |

- A ticket with no assignee cannot move to `in_progress`.
- Skipping a step or moving backwards is rejected.
- A resolved ticket cannot be modified (including assignment) until it is reopened.

## Work queue

Shows `open` tickets ordered `critical` -> `high` -> `medium` -> `low`. Tickets with the same
priority are ordered by the earlier numeric ticket ID (`T2` before `T10`).
`in_progress` and `resolved` tickets are not listed.

## Reports

Total ticket count plus counts by status and by priority. Every category is shown, with 0
when unused, so an empty system still gives a valid report.

## Where tickets are saved

Tickets are saved to `data/tickets.json` after every successful change and loaded on startup.

- **Start fresh:** delete `data/tickets.json` (or move it aside).
- **Missing file:** the app starts with no tickets.
- **Corrupted file:** the app refuses to start and tells you why. It never overwrites a file it
  cannot read, so no data is silently erased.
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
| `tests/test_storage.py` | save/reload, missing file, corrupted JSON, unique IDs after reload |
| `tests/test_cli.py` | scripted full menu sessions, restart, corrupted file at startup |

## Project layout

```
main.py                  entry point
campusflow/
  tickets.py             create, validation, priority, assign, list/view
  workflow.py            status transitions, reopen
  work_queue.py          priority-sorted open queue
  reports.py             totals and breakdowns
  storage.py             JSON load/save
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
- Tickets cannot be deleted or edited except for assignment and status.

## Pull requests

- Engineer A PR: _link_
- Engineer B PR: _link_
