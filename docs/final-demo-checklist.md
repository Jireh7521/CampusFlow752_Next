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

## Manual application scenarios

Use disposable local test data; do not use real support-ticket data for the demonstration.

| Scenario | Steps / input | Expected behavior | Actual observation | Pass / fail |
|---|---|---|---|---|
| Interactive startup using module entry point | From a temporary working directory, run `PYTHONPATH="$REPO" python3 -m campusflow.cli` | Application starts, offers first-account setup when no account exists, then displays the menu | On 2026-10-15, the CLI displayed “No CampusFlow account exists. Create the first account.”, accepted the demo-account setup, and reached the 12-option menu. The demo ran from a temporary directory, separate from the repository's existing data. | PASS |
| Interactive startup using `main.py` | Run `python3 main.py` from the repository root with disposable data | Application starts and displays the authentication/menu flow | Not separately observed in this session. | NOT RUN |
| Priority calculation | Create a high-urgency ticket affecting 10 or more users | Priority is `critical` | Created T002 (Campus WiFi Network Failure), category Network, urgency high, affected users 15; application returned priority `critical`. | PASS |
| Invalid input safety | Attempt ticket creation with affected users `0`, then view/list tickets | Invalid input is rejected; no ticket is created by the rejected attempt |  |  |
| Assignment rule | Move an unassigned ticket to `in_progress` | Action is rejected and status remains unchanged | Attempted to move unassigned T001 to `in_progress`; application rejected it with: `Ticket T001 is unassigned. Assign it before moving it to in_progress.` | PASS |
| Resolved-ticket protection | Resolve a ticket, then try to assign it or add a note | Modification is rejected until reopening |  |  |
| Reopen workflow | Reopen a resolved ticket and then add a note | Status returns to `open`; note can be added |  |  |
| Combined search | Search a title substring and supply category, status, and priority filters | Only tickets matching every supplied filter are shown | Searched title `Campus WiFi` with category `network`; T002 was returned. Status and priority filters were left blank, so the full multi-filter combination remains unverified. | PARTIAL |
| Invalid search filter | Enter an invalid category/status/priority filter | A clear error is shown and the CLI prompts again |  |  |
| Priority-sorted search | Use the priority-sorted search option with several priorities and IDs | Results are ordered by priority, then numeric ticket ID |  |  |
| Open work queue | Use the work-queue option after adding tickets in different statuses | Only eligible open tickets appear | After T002 moved to `in_progress`, the queue showed open T001 and omitted T002. | PASS |
| Report metrics | View reports with at least two tickets, then resolve and reopen one | Totals, category/status/priority counts, and resolution percentage reflect current statuses | Before resolving T002: total 2; open 1; in_progress 1; resolved 0; critical 1; medium 1; Network 1; Other 1; unresolved 2; resolution 0%. Post-resolve/reopen report behavior was not tested. | PARTIAL |
| Follow-up notes | Add two notes to a ticket, view it, restart the application | Notes appear in note-ID order and persist after restart | Added one follow-up note to T002; application confirmed `Added note to T002.` Multiple-note ordering and persistence across restart were not tested. | PARTIAL |
| ID continuity | Create a ticket and note, restart, then create another ticket and another note on the original ticket | Ticket IDs remain unique across restarts; note IDs continue sequentially per ticket |  |  |
| Empty report | Run Reports when no tickets exist | Counts are zero and resolution percentage is 0%; no exception occurs |  |  |
| Corrupt JSON safety | In a disposable copy, replace the data file with invalid JSON and start the app | Startup fails safely and does not overwrite the corrupt file |  |  |
| Engineering Understanding Check | Run the six-question check and explain at least two answers with code examples | Score is out of six; two nonblank explanations are provided and relevant source files are identified | Engineer B completed the six-question check on commit `0a953cf4f01fad676e89a343649bf1476c5589d4`; score 5/6. Q1 explanation cited `campusflow/storage.py` and `StorageError` for malformed JSON; Q2 explanation cited `campusflow/workflow.py` and the unassigned-ticket guard in `change_status`. Invalid-answer/blank-explanation retry behavior was not separately verified. | PARTIAL |

## Git collaboration and review evidence

Record links and facts only after they happen. Do not self-approve a pull request or claim a review that was not performed.

| Evidence | Link / observed details |
|---|---|
| Engineer A implementation-and-test PR | [PR #24](https://github.com/Jireh7521/CampusFlow752_Next/pull/24) — local authentication; [PR #19](https://github.com/Jireh7521/CampusFlow752_Next/pull/19) — JSON validation and ID continuity. |
| Engineer B implementation-and-test PR | [PR #25](https://github.com/Jireh7521/CampusFlow752_Next/pull/25) — persisted-ticket validation tests; [PR #30](https://github.com/Jireh7521/CampusFlow752_Next/pull/30) — combined search CLI tests. |
| Engineer A review of Engineer B PR | `Jireh7521` approved [PR #43](https://github.com/Jireh7521/CampusFlow752_Next/pull/43) on 2026-10-15. Feedback praised the 124-test evidence and source-based quiz explanations; requested follow-up verification of quiz retries, ID continuity after restart, empty reports, and corrupt-JSON safety. |
| Engineer B review of Engineer A PR | `bridgetukpoju01-droid` approved [PR #42](https://github.com/Jireh7521/CampusFlow752_Next/pull/42) on 2026-10-15. Feedback praised evidence-based source/test references, the distinction between simulated exceptions and untested power-loss/process-crash behavior, and avoiding false local-test claims. |
| Changes made in response to review feedback | PR #42's learning-cycle entry was merged with the narrowed atomic-save claim and explicit testing limitation. PR #43's quiz evidence was merged and marks retry behavior unverified. Additional manual follow-ups requested on PR #43 remain unverified. |
| README contribution summaries confirmed by both fellows | PENDING. Both fellows must reply with explicit confirmation or corrections on [Issue #10](https://github.com/Jireh7521/CampusFlow752_Next/issues/10); neither confirmation is inferred from PR approval. |

## Remaining defects and limitations

Record any failed scenario, defect, workaround, or limitation honestly. If no defect was observed, write that the scenario was tested and no defect was observed; do not generalize from untested scenarios.

| Scenario / defect | Reproduction steps | Observed result | Follow-up issue / PR |
|---|---|---|---|
|  |  |  |  |

## Engineer B demo notes — observed on 2026-10-15

- Earlier tested commit: `9ac8e10b3ff0c5994e98c9e2621e82ef83469484`; Python 3.12.3; 123 tests ran in 19.058 seconds and finished `OK` (0 failures, 0 errors).
- Latest local test: pulled main through commit `f6058100a08e2962cdfba93a9d1946f48ceff2cd`; Python 3.12.3; 124 tests ran in 19.844 seconds and finished `OK` (0 failures, 0 errors).
- Manual flow previously verified startup and demo-account creation, ticket listing, assigning T002 to `demo_user`, moving assigned T002 to `in_progress`, adding one follow-up note, and resolving T002.
- In this session, the module CLI entry point was launched from a temporary directory. The first-account prompt appeared, the account setup was completed, and the 12-option menu appeared. This verifies startup/menu display for `python3 -m campusflow.cli`; it does not complete the remaining manual scenarios or independently verify `python3 main.py`.
- Engineering Understanding Check: Engineer B completed the six-question quiz on commit `0a953cf4f01fad676e89a343649bf1476c5589d4`, scored 5/6, and submitted two explanations for mentor discussion. Q1: `campusflow/storage.py` raises `StorageError` for malformed JSON so corrupted data is not silently treated as an empty list. Q2: `campusflow/workflow.py` rejects a transition to `in_progress` when the ticket has no assignee.
- These notes record only observed steps. Unrun scenarios remain blank, NOT RUN, or PARTIAL; they are not implied to have passed.
- Current CI evidence: after PR #44 merged, GitHub Actions run [#38766963927](https://github.com/Jireh7521/CampusFlow752_Next/actions/runs/38766963927) passed the full unit-test job on Python 3.8, 3.11, and 3.12 for main commit `f6058100a08e2962cdfba93a9d1946f48ceff2cd`. This is CI evidence, not a fresh-clone run or a full interactive demonstration.
