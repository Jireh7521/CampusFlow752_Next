# Design decisions

Agreed interfaces for CampusFlow. Keep this file short and update it if the team changes a decision.

## Ownership

| Area | Module | Owner |
|------|--------|-------|
| F1 Create, validation, priority engine | `campusflow/tickets.py` | Engineer A |
| F3 Assign | `campusflow/tickets.py` | Engineer A / B (agree) |
| F4 Workflow and reopen | `campusflow/workflow.py` | Engineer B |
| F5 Work queue | `campusflow/work_queue.py` | Engineer B |
| F6 Reports | `campusflow/reports.py` | Engineer B |
| F7 JSON persistence | `campusflow/storage.py` | Both |
| Authentication | `campusflow/auth.py` | Both |
| CLI menu | `campusflow/cli.py`, `main.py` | Both |

> Fill in the real names and adjust the owners above to match what you agreed.

## Function contracts

1. **Ticket collection:** a plain `list` of `dict`s, passed into every function as the first argument. There is no global state, so tests can build their own list.
2. **Errors:** invalid input or an illegal move raises `ValueError` with a human-readable message. The CLI catches it and prints `Error: <message>`. Storage problems raise `StorageError`, a subclass of `ValueError`.
3. **No half-changes:** every function validates first and changes the ticket last, so a rejected call leaves the ticket untouched.
4. **Return values:** create / assign / change status / reopen return the updated ticket dict. `get_work_queue` returns a new sorted list. `build_report` returns a dict. Display helpers (`format_*`) return strings; only the CLI prints.
5. **Persistence:** `storage.py` owns JSON. `load_tickets(path)` returns a list (`[]` if the file is missing) and `save_tickets(tickets, path)` writes it. The CLI saves after every successful change.
6. **Testing without a keyboard:** business logic never calls `input()`. The CLI takes `input_fn` / `print_fn` arguments so tests can script a whole session. Password entry is injected separately through `password_fn`.
7. **Authentication:** the CLI creates a first local account when no account file exists, then requires username/password login on later runs. `auth.py` stores salted PBKDF2-HMAC-SHA256 hashes (600,000 iterations) in `data/users.json`; it never stores plaintext passwords. Account data is validated and saved atomically.

## Rules we chose

- **IDs:** `T` + number padded to 3 digits. The next ID is the highest existing number + 1, so IDs stay unique after a reload.
- **Normalization:** category and urgency accept any letter case and surrounding spaces. IDs and status names are also case/space tolerant.
- **Resolved tickets:** cannot be assigned or moved anywhere except `open` (reopen). `workflow.ensure_modifiable()` is the shared guard.
- **Work queue:** contains tickets with status `open` only. Tie-break is the numeric part of the ID.
- **Reports:** always show every status and priority, with 0 where unused.
- **Corrupted data:** the app refuses to start rather than overwrite a file it cannot read. A temp-file-then-rename save prevents half-written files. This applies to both ticket and account data.
- **Authentication scope:** authentication protects the normal local CLI path; it is not multi-user role authorization and cannot protect local files from someone with direct access to the computer.
