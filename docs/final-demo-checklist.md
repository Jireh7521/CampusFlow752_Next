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
| `python3 -m unittest discover -s tests -v` | 123 tests ran in 19.898s; OK; 0 failures, 0 errors | PASS | Engineer B / 2026-10-15 |
| Commit SHA tested locally | `70a8907baaba179c224fc2afc04a9aa83903b794` | PASS | Engineer B / 2026-10-15 |
| GitHub Actions run [#38749006848](https://github.com/Jireh7521/CampusFlow752_Next/actions/runs/38749006848), PR head commit `4da2cdf4fd18e812bb51cc361655c3cb3cc13334` | Python 3.8, 3.11, and 3.12 unit-test jobs all completed successfully | PASS | GitHub Actions / 2026-10-15 |

## Manual application scenarios

Start with `python3 main.py`. Use disposable local test data; do not use real support-ticket data for the demonstration.

| Scenario | Steps / input | Expected behavior | Actual observation | Pass / fail |
|---|---|---|---|---|
| Priority calculation | Create a high-urgency ticket affecting 10 or more users | Priority is `critical` |  |  |
| Invalid input safety | Attempt ticket creation with affected users `0`, then view/list tickets | Invalid input is rejected; no ticket is created by the rejected attempt |  |  |
| Assignment rule | Move an unassigned ticket to `in_progress` | Action is rejected and status remains unchanged |  |  |
| Resolved-ticket protection | Resolve a ticket, then try to assign it or add a note | Modification is rejected until reopening |  |  |
| Reopen workflow | Reopen a resolved ticket and then add a note | Status returns to `open`; note can be added |  |  |
| Combined search | Search a title substring and supply category, status, and priority filters | Only tickets matching every supplied filter are shown |  |  |
| Invalid search filter | Enter an invalid category/status/priority filter | A clear error is shown and the CLI prompts again |  |  |
| Priority-sorted search | Use the priority-sorted search option with several priorities and IDs | Results are ordered by priority, then numeric ticket ID |  |  |
| Open work queue | Use the work-queue option after adding tickets in different statuses | Existing queue behavior is retained; only eligible open tickets appear |  |  |
| Report metrics | View reports with at least two tickets, then resolve and reopen one | Totals, category/status/priority counts, and resolution percentage reflect current statuses |  |  |
| Follow-up notes | Add two notes to a ticket, view it, restart the application | Notes appear in note-ID order and persist after restart |  |  |
| ID continuity | Create a ticket and note, restart, then create another ticket and another note on the original ticket | Ticket IDs remain unique across restarts; note IDs continue sequentially per ticket |  |  |
| Empty report | Run Reports when no tickets exist | Counts are zero and resolution percentage is 0%; no exception occurs |  |  |
| Corrupt JSON safety | In a disposable copy, replace the data file with invalid JSON and start the app | Startup fails safely and does not overwrite the corrupt file |  |  |
| Engineering Understanding Check | Run the six-question check; submit an invalid answer and blank explanations before valid answers | Invalid entries trigger retries; score is out of six; two nonblank explanations are shown |  |  |

## Git collaboration and review evidence

Record links and facts only after they happen. Do not self-approve a pull request or claim a review that was not performed.

| Evidence | Link / observed details |
|---|---|
| Engineer A implementation-and-test PR |  |
| Engineer B implementation-and-test PR |  |
| Engineer A review of Engineer B PR (reviewer, date, substantive feedback) |  |
| Engineer B review of Engineer A PR (reviewer, date, substantive feedback) |  |
| Changes made in response to review feedback |  |
| README contribution summaries confirmed by both fellows |  |

## Remaining defects and limitations

Record any failed scenario, defect, workaround, or limitation honestly. If no defect was observed, write that the scenario was tested and no defect was observed; do not generalize from untested scenarios.

| Scenario / defect | Reproduction steps | Observed result | Follow-up issue / PR |
|---|---|---|---|
|  |  |  |  |
