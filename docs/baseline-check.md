# CampusFlow Next — Baseline Check

**Date:** 2026-10-14  
**Purpose:** Record the existing application's behavior before making changes for the CampusFlow Next reliability, search, and engineering-quality sprint.

## Environment and commands

- Application command: `python3 main.py`
- Automated test command: `python3 -m unittest discover -s tests -v`
- Test result: **65 tests passed; 0 failures; 0 errors**.
- Runtime reported by unittest: **0.037 seconds**.
- The repository README states that the project uses Python 3.8+ and the standard library.

## Manual checks performed

| Check | Input or action | Observed result | Assessment |
|---|---|---|---|
| Reject invalid affected-user count | Started ticket creation, entered title `0`, category `other`, urgency `low`, and affected users `0` | The app displayed: `Affected users must be a positive whole number (1 or more).` | Passed for this input; no ticket was created from this attempt. |
| Create a valid ticket | Title `Laptop`, category `Hardware`, urgency `medium`, affected users `1` | The app reported: `Created T002 with priority 'medium'.` | Passed for this input. |
| Check persistence after restart | Exited and restarted the app, then chose **2 — List all tickets** | The list showed both `T001` and `T002`. | Persistence confirmed for these tickets in this manual check. |

## Automated coverage observed

The existing test suite includes tests for:

- Ticket field validation and priority boundaries, including high urgency with 12 affected users producing critical priority.
- Saving and reloading tickets, restart behavior, and sequential/unique IDs.
- Invalid or corrupted JSON, duplicate IDs, and unexpected collection shapes.
- Assignment rules, status transitions, and reopening resolved tickets.
- Work-queue priority ordering and numeric ticket-ID tie-breaking.
- Report totals, category/status-related validation, and empty reports.
- CLI input handling and preservation of saved data after failed actions.

## Findings versus confirmed defects

### Confirmed observations

- The existing automated suite passes: 65 tests, with no failures or errors.
- The application rejected the tested zero-user input.
- The application created `T002` for the tested valid input.
- The application showed `T001` and `T002` after a restart.

### Potential concerns requiring further investigation

- These checks cover only a limited set of manual inputs and the existing automated tests. They do not prove that all edge cases or all sprint audit concerns are resolved.
- Any additional reported defect should be reproduced and its actual output recorded before it is described as confirmed.

### Confirmed defects

**None confirmed by the checks recorded in this baseline report.** This means no defect was reproduced in the checks above; it does not mean that no defects exist.

## Baseline conclusion

The current application and test suite provide a passing starting point for subsequent changes. Keep this baseline as evidence of pre-change behavior, and rerun the full test command after each relevant change to compare results.
