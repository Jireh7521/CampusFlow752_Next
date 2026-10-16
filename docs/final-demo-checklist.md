# Final demonstration and verification checklist

Use this checklist during a fresh-clone demonstration. **Do not mark a scenario as passed until someone runs it and records the observed result.** This document is a plan, not evidence that a command or manual scenario has already passed.

## Environment and automated tests

- [ ] Clone the repository into a clean directory:
  `git clone https://github.com/Jireh7521/CampusFlow752_Next.git`
- [ ] Change into the repository:
  `cd CampusFlow752_Next`
- [x] Record the Python version: `python3 --version`
- [x] Run the full suite: `python3 -m unittest discover -s tests -v`
- [x] Record the exact test count, failures/errors, and commit SHA below.

| Command / commit | Actual observed result | Pass / fail | Run by / date |
|---|---|---|---|
| `python3 --version` | Python 3.12.3 | PASS | Engineer B / 2026-10-15 |
| `python3 -m unittest discover -s tests -v` | 123 tests ran in 19.058s; OK; 0 failures, 0 errors | PASS | Engineer B / 2026-10-15 |
| Commit SHA tested locally | `9ac8e10b3ff0c5994e98c9e2621e82ef83469484` | PASS | Engineer B / 2026-10-15 |
| `python3 -m unittest discover -s tests -v` on main | 124 tests ran in 21.655s; OK; 0 failures, 0 errors | PASS | Engineer B / 2026-10-15 |
| Main commit for the previous 124-test run and quiz | `0a953cf4f01fad676e89a343649bf1476c5589d4` | PASS | Engineer B / 2026-10-15 |
| `python3 -m unittest discover -s tests -v` after pulling current main | 124 tests ran in 19.844s; OK; 0 failures, 0 errors | PASS | Engineer B / 2026-10-15 |
| Current main commit used for the latest local test run | `f6058100a08e2962cdfba93a9d1946f48ceff2cd` | PASS | Engineer B / 2026-10-15 |
| GitHub Actions run [#38749006848](https://github.com/Jireh7521/CampusFlow752_Next/actions/runs/38749006848), PR head commit `4da2cdf4fd18e812bb51cc361655c3cb3cc13334` | Python 3.8, 3.11, and 3.12 unit-test jobs all completed successfully | PASS | GitHub Actions / 2026-10-15 |
| GitHub Actions run [#38766963927](https://github.com/Jireh7521/CampusFlow752_Next/actions/runs/38766963927), main commit `f6058100a08e2962cdfba93a9d1946f48ceff2cd` | Python 3.8, 3.11, and 3.12 full unit-test jobs all completed successfully after PR #44 merged | PASS | GitHub Actions / 2026-10-15 |
| GitHub Actions run [#38921909603](https://github.com/Jireh7521/CampusFlow752_Next/actions/runs/38921909603), PR #50 head commit `3d13b3b0f9fac12b89d12f44653dc827e2d3016c` | Python unit-test workflow passed for the `main.py` entry-point regression test and updated evidence map. The run does not establish that `python3 main.py` was manually launched. | PASS (automated test only) | GitHub Actions / 2026-10-16 |

## Manual application scenarios

Use disposable local test data; do not use real support-ticket data for the demonstration.

| Scenario | Steps / input | Expected behavior | Actual observation | Pass / fail |
|---|---|---|---|---|
| Interactive startup using module entry point | From a temporary working directory, run `PYTHONPATH="$REPO" python3 -m campusflow.cli` | Application starts, offers first-account setup when no account exists, then displays the menu | On 2026-10-15, the CLI displayed “No CampusFlow account exists. Create the first account.”, accepted the demo-account setup, and reached the 12-option menu. The demo ran from a temporary directory, separate from the repository's existing data. | PASS |
| Interactive startup using `main.py` | Run `python3 main.py` from the repository root with disposable data | Application starts and displays the authentication/menu flow | Not separately observed in this session. | NOT RUN |
| Priority calculation | Create a high-urgency ticket affecting 10 or more users | Priority is `critical` | Created T002 (Campus WiFi Network Failure), category Network, urgency high, affected users 15; application returned priority `critical`. | PASS |
| Invalid input safety | Attempt ticket creation with affected users `0`, then view/list tickets | Invalid input is rejected; no ticket is created by the rejected attempt | On 2026-10-16, entered affected users `0`; the CLI rejected it with `Affected users must be a positive whole number (1 or more).` Listing tickets then showed `No tickets yet.` | PASS |
| Assignment rule | Move an unassigned ticket to `in_progress` | Action is rejected and status remains unchanged | Attempted to move unassigned T001 to `in_progress`; application rejected it with: `Ticket T001 is unassigned. Assign it before moving it to in_progress.` | PASS |
| Resolved-ticket protection | Resolve a ticket, then try to assign it or add a note | Modification is rejected until reopening | On 2026-10-16, attempted to assign resolved T001 to another user; the CLI rejected the operation and instructed the user to reopen the ticket first. Adding a note while resolved was not separately tested. | PASS |
| Reopen workflow | Reopen a resolved ticket and then add a note | Status returns to `open`; note can be added | On 2026-10-16, reopened resolved T001 successfully and added follow-up notes while it was open. | PASS |
| Combined search | Search a title substring and supply category, status, and priority filters | Only tickets matching every supplied filter are shown | On 2026-10-16, searched title `network`, category `network`, status `open`, and priority `critical`; T001 matched all four filters. | PASS |
| Invalid search filter | Enter an invalid category/status/priority filter | A clear error is shown and the CLI prompts again | On 2026-10-16, entered invalid status `cllosed`; the CLI rejected it and prompted again. Entering valid filters returned the matching ticket. | PASS |
| Priority-sorted search | Use the priority-sorted search option with several priorities and IDs | Results are ordered by priority, then numeric ticket ID | On 2026-10-16, results appeared in descending priority order: T001 critical, T002 medium, T003 low. Equal-priority tie-breaking by numeric ID was not separately tested. | PARTIAL |
| Open work queue | Use the work-queue option after adding tickets in different statuses | Only eligible open tickets appear | After T002 moved to `in_progress`, the queue showed open T001 and omitted T002. | PASS |
| Report metrics | View reports with at least two tickets, then resolve and reopen one | Totals, category/status/priority counts, and resolution percentage reflect current statuses | On 2026-10-16, report for T001 showed open 1 and resolution 0%; after resolving it, resolved 1 and resolution 100%; after reopening it, open 1, unresolved 1, and resolution 0%. The full resolve/reopen sequence with multiple tickets was not tested. | PARTIAL |
| Follow-up notes | Add two notes to a ticket, view it, restart the application | Notes appear in note-ID order and persist after restart | On 2026-10-16, added notes N001 and N002 to T001. Both appeared in order when viewing the ticket and remained available after restarting the application. | PASS |
| ID continuity | Create a ticket and note, restart, then create another ticket and another note on the original ticket | Ticket IDs remain unique across restarts; note IDs continue sequentially per ticket | On 2026-10-16, created T001, T002, and T003 sequentially and confirmed all three loaded after restart. Creating T004 after restart and verifying continued note-ID sequence were not tested. | PARTIAL |
| Empty report | Run Reports when no tickets exist | Counts are zero and resolution percentage is 0%; no exception occurs | On 2026-10-16, ran the report with no tickets; total, status, priority, category, unresolved, and resolved counts were zero, and resolution percentage was 0%. | PASS |
| Corrupt JSON safety | In a disposable copy, replace the data file with invalid JSON and start the app | Startup fails safely and does not overwrite the corrupt file | On 2026-10-16, startup displayed a clear invalid-JSON error, refused to continue, and reported that the file was not changed. The malformed contents remained in the disposable test file. | PASS |
| Engineering Understanding Check | Run the six-question check and explain at least two answers with code examples | Score is out of six; two nonblank explanations are provided and relevant source files are identified | On 2026-10-16, first attempt scored 6/6 and two code-based explanations were submitted. A second attempt with one deliberately incorrect answer scored 5/6; the check continued to the next question, counted the wrong answer, accepted two explanations, and returned to the menu. Automatic retry after a wrong answer was not observed. | PASS |


## Automated regression coverage related to manual scenarios

The tests below provide repeatable regression coverage for several behaviors that are only partly or not yet observed in the live manual demo. **Automated coverage is not a claim that the corresponding interactive scenario was manually demonstrated.** Keep the manual table above marked PARTIAL or NOT RUN until the actual demo is observed.

| Behavior | Automated evidence | Boundary / manual follow-up |
|---|---|---|
| `main.py` entry-point dispatch | `tests/test_cli.py::test_main_py_entrypoint_invokes_cli_and_propagates_exit_code` verifies the script calls the CLI and propagates its exit code. | Does not prove a human-facing interactive startup works in a terminal; the separate manual startup row remains NOT RUN. |
| Equal-priority numeric ticket-ID tie-break | `tests/test_tickets.py::test_priority_sort_uses_priority_then_numeric_ticket_id` | Covers ordering logic in a unit test; the live equal-priority search scenario remains PARTIAL. |
| Multi-ticket report through resolve/reopen | `tests/test_reports_cli.py::test_report_cli_shows_breakdowns_and_tracks_resolve_reopen` | Covers a two-ticket report and resolution percentage; the live manual sequence remains PARTIAL. |
| Note-ID continuity after save/load | `tests/test_notes.py::test_notes_and_note_id_continuity_survive_save_and_load` | Covers persisted notes and the next note ID after reload; the live T004/note-ID scenario remains PARTIAL. |
| Adding a note to a resolved ticket | `tests/test_notes.py::test_notes_survive_resolution_and_reopening` | Confirms the operation is rejected until reopening; the separate live CLI attempt remains unverified. |
| Quiz invalid-answer retry and explanation validation | `tests/test_engineering_check.py` includes invalid-choice and explanation validation tests. | Automated tests do not establish a complete live demo by both fellows; Engineer A's independent demonstration still needs evidence. |


## Git collaboration and review evidence

Record links and facts only after they happen. Do not self-approve a pull request or claim a review that was not performed.

| Evidence | Link / observed details |
|---|---|
| Engineer A implementation-and-test PR | [PR #24](https://github.com/Jireh7521/CampusFlow752_Next/pull/24) — local authentication; [PR #19](https://github.com/Jireh7521/CampusFlow752_Next/pull/19) — JSON validation and ID continuity. |
| Engineer B implementation-and-test PR | [PR #25](https://github.com/Jireh7521/CampusFlow752_Next/pull/25) — persisted-ticket validation tests; [PR #30](https://github.com/Jireh7521/CampusFlow752_Next/pull/30) — combined search CLI tests. |
| Engineer A review of Engineer B PR | `Jireh7521` approved [PR #43](https://github.com/Jireh7521/CampusFlow752_Next/pull/43) on 2026-10-15. Feedback praised the 124-test evidence and source-based quiz explanations; requested follow-up verification of quiz retries, ID continuity after restart, empty reports, and corrupt-JSON safety. |
| Engineer B review of Engineer A PR | `bridgetukpoju01-droid` approved [PR #42](https://github.com/Jireh7521/CampusFlow752_Next/pull/42) on 2026-10-15. Feedback praised evidence-based source/test references, the distinction between simulated exceptions and untested power-loss/process-crash behavior, and avoiding false local-test claims. |
| Changes made in response to review feedback | PR #42's learning-cycle entry was merged with the narrowed atomic-save claim and explicit testing limitation. PR #43's quiz evidence was merged and marks retry behavior unverified. Additional manual follow-ups requested on PR #43 remain unverified. |
| README contribution summaries | Engineer B explicitly confirmed their own summary with no corrections in [Issue #10 comment](https://github.com/Jireh7521/CampusFlow752_Next/issues/10#issuecomment-6218407445). Engineer A's separate confirmation/corrections remain PENDING; PR approval is not treated as personal confirmation. |

## Remaining defects and limitations

Record any failed scenario, defect, workaround, or limitation honestly. If no defect was observed, write that the scenario was tested and no defect was observed; do not generalize from untested scenarios.

| Scenario / defect | Reproduction steps | Observed result | Follow-up issue / PR |
|---|---|---|---|
|  |  |  |  |

## Additional observations — 2026-10-16

- Fresh temporary-directory empty-report check: launched the module CLI from an isolated temporary working directory, created a demo account, selected Report (option 8), and observed total tickets 0; status, priority, and category counts all 0; unresolved and resolved counts 0; resolution percentage 0%. No exception occurred. This confirms the empty-report scenario for this run.
- Search with no matches: selected Search tickets (option 10), entered title substring `john` and category text `Ot`, left status and priority blank, and observed `No matching tickets found.` Because `Ot` is not one of the documented category values, this observation does **not** establish how invalid category filters are validated. Invalid-filter retry remains to be tested separately.
- These additional observations do not satisfy the outstanding live demonstrations: `python3 main.py` startup; numeric ticket-ID tie-breaking for at least two equal-priority tickets; report metrics with multiple tickets before and after resolve/reopen; creating T001–T003, restarting, creating T004, adding another note to an earlier ticket, and restarting to verify ID continuity; rejection of a note while a ticket is resolved followed by successful note creation after reopening; and the quiz invalid-answer/blank-explanation retry plus Engineer A's independent demonstration and code explanations.
- README contribution summaries still require explicit confirmation or correction from both fellows in [Issue #10](https://github.com/Jireh7521/CampusFlow752_Next/issues/10). No personal confirmation is inferred from PR approvals.

## Engineer B demo notes — observed on 2026-10-15 and 2026-10-16

- Earlier tested commit: `9ac8e10b3ff0c5994e98c9e2621e82ef83469484`; Python 3.12.3; 123 tests ran in 19.058 seconds and finished `OK` (0 failures, 0 errors).
- Latest local test: pulled main through commit `f6058100a08e2962cdfba93a9d1946f48ceff2cd`; Python 3.12.3; 124 tests ran in 19.844 seconds and finished `OK` (0 failures, 0 errors).
- Manual flow previously verified startup and demo-account creation, ticket listing, assigning T002 to `demo_user`, moving assigned T002 to `in_progress`, adding one follow-up note, and resolving T002.
- In this session, the module CLI entry point was launched from a temporary directory. The first-account prompt appeared, the account setup was completed, and the 12-option menu appeared. This verifies startup/menu display for `python3 -m campusflow.cli`; it does not complete the remaining manual scenarios or independently verify `python3 main.py`.
- Engineering Understanding Check: Engineer B completed the six-question quiz on commit `0a953cf4f01fad676e89a343649bf1476c5589d4`, scored 5/6, and submitted two explanations for mentor discussion. Q1: `campusflow/storage.py` raises `StorageError` for malformed JSON so corrupted data is not silently treated as an empty list. Q2: `campusflow/workflow.py` rejects a transition to `in_progress` when the ticket has no assignee.
- These notes record only observed steps. Unrun scenarios remain blank, NOT RUN, or PARTIAL; they are not implied to have passed.
- Additional manual checks observed on 2026-10-16: rejected affected-users value `0` without creating a ticket; resolved-ticket assignment was blocked; T001 was reopened; combined title/category/status/priority search returned the matching ticket; invalid status filter was rejected and prompted again; priority-sorted results showed critical, medium, then low; reports showed 0% before resolution, 100% after resolution, and 0% after reopening; two follow-up notes persisted across restart; empty report returned zero counts and 0%; malformed JSON caused a clear safe-stop; Engineering Understanding Check scored 6/6 on the first attempt and 5/6 after one deliberately incorrect answer on the second attempt. See the manual scenario table for limitations still marked PARTIAL or NOT RUN.
- CI evidence: after PR #44 merged, GitHub Actions run [#38766963927](https://github.com/Jireh7521/CampusFlow752_Next/actions/runs/38766963927) passed the full unit-test job on Python 3.8, 3.11, and 3.12 for main commit `f6058100a08e2962cdfba93a9d1946f48ceff2cd`. PR #50 was subsequently approved by Engineer A and merged at `41662ca414b457ddc966da67bc92a52b17cd04ba`; its Python unit-test workflow [#38921909603](https://github.com/Jireh7521/CampusFlow752_Next/actions/runs/38921909603) passed. These are CI results, not a fresh-clone run or a full interactive demonstration.
