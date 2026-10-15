# AI learning log

**This file is a template. Do not submit it as-is.** The guide requires each fellow to record at least three *real* AI learning interactions, including one where you corrected, improved or rejected an AI suggestion after checking it. Fill these in with what actually happened, in your own words. Invented entries count against you.

## Recorded team example: AI-assisted report documentation corrected after source inspection

**Scope:** This is one real shared correction from the repository audit. It is not a substitute for each fellow's own learning cycles or independent reflection.

- **Concept gap:** The first README report description did not mention category counts, unresolved/resolved totals, or resolution percentage.
- **Prompt available in this audit record:** “audit the work”. The earlier prompt that produced the first README wording was not preserved, so it is not reconstructed here as a quote.
- **AI-generated wording reviewed:** “Reports show total ticket count and counts by every status and priority, including zero counts. Empty reports are supported.”
- **Independent verification:** Inspected `campusflow/reports.py` and `tests/test_reports.py`. The report model includes category breakdowns, unresolved/resolved totals, and resolution percentage; tests cover empty reports and counts after resolve/reopen operations. The full suite later passed 120 tests on Python 3.8, 3.11, and 3.12 in [GitHub Actions run #38729201820](https://github.com/Jireh7521/CampusFlow752_Next/actions/runs/38729201820).
- **Decision:** Improved the README wording in [PR #28](https://github.com/Jireh7521/CampusFlow752_Next/pull/28) to document all implemented metrics and the empty-report 0% case.
- **Reflection:** The initial wording described only part of the feature. Checking the source and regression tests showed the documentation was incomplete, so it was revised rather than accepted as-is.
- **Regression guard:** `tests/test_reports.py`, especially the empty-report, known-fixture, resolve/reopen, and formatted-output tests.

Each fellow should discuss this example and add their own real interactions below. Do not claim this shared example as a personal experiment unless you personally performed and can explain the verification.

---

Ideas for real experiments that fit this project (do them yourself, predict first, then run):

- `sorted()` with a tuple key: predict the order of `[("high", 10), ("high", 2)]` as strings vs numbers (why `"T10" < "T2"`).
- A dict of sets as a state table: write a traffic-light example and test a legal and an illegal move.
- `unittest.assertRaises` as a context manager: write a test that should fail, watch it fail, then fix it.
- `json.load` on a broken file: see which exception you get.
- Why `bool` is a subclass of `int` in Python (`isinstance(True, int)`), and what that means for validating "positive integer".

Template per entry:

```
## Fellow: <your name>
### Interaction #N — <concept/topic>
Problem:
My initial understanding:
Prompt to AI:
Useful AI guidance:
My independent experiment/test:
Verification source or result:
Decision: (accepted / improved / rejected, and why)
Related file/commit:
What I can now explain without AI:
```

---

## Fellow: bridgetukpoju01-droid (Engineer B)

### Interaction #1 — Python booleans and integer validation

**Problem:** Understand why validating a positive integer using only `isinstance(value, int)` can accept a boolean as a user count.

**My initial understanding:** I expected `True` not to pass an integer check.

**Prompt to AI:** The exact original wording was not preserved, so I am recording the topic rather than inventing a quotation.

**Useful AI guidance:** In Python, `bool` is a subclass of `int`. A validator should explicitly reject booleans before accepting integers, and should enforce the required minimum.

**My experiment:**
```python
print("Is True an integer?", isinstance(True, int))
print("Is 5 an integer?", isinstance(5, int))
print("Is 5.0 an integer?", isinstance(5.0, int))
```

**Observed result:**
```text
Is True an integer? True
Is 5 an integer? True
Is 5.0 an integer? False
```

**Verification source or result:** The output above was observed when I ran the experiment. The repository's affected-user validation and regression tests also cover boolean, float, zero, and negative values.

**Decision:** Improved the validation approach by treating booleans separately rather than relying on `isinstance(value, int)` alone.

**Related code:** `campusflow/tickets.py` and the affected-users validation tests.

**What I can now explain without AI:** Python treats `True` as an integer subtype, so an integer type check alone is not enough to validate a positive user count.

### Interaction #2 — Lexicographic sorting versus numeric ticket IDs

**Problem:** Understand why sorting ticket IDs as strings can put `T10` before `T2`.

**My initial understanding:** I expected the ticket IDs to sort in numeric order.

**Prompt to AI:** The exact original wording was not preserved, so I am recording the topic rather than inventing a quotation.

**Useful AI guidance:** String sorting compares characters lexicographically. To sort ticket IDs numerically, extract and convert the numeric suffix before comparing.

**My experiment:**
```python
tickets = [("high", "T10"), ("high", "T2")]
print("String sorting:")
print(sorted(tickets, key=lambda ticket: (ticket[0], ticket[1])))
print("\nNumeric ticket-ID sorting:")
print(sorted(tickets, key=lambda ticket: (ticket[0], int(ticket[1][1:]))))
```

**Observed result:**
```text
String sorting:
[('high', 'T10'), ('high', 'T2')]

Numeric ticket-ID sorting:
[('high', 'T2'), ('high', 'T10')]
```

**Verification source or result:** The output above was observed when I ran the experiment. The repository includes `test_priority_sort_uses_priority_then_numeric_ticket_id` to protect the intended behavior.

**Decision:** Use the numeric ticket-ID key so IDs sort in numeric order within each priority.

**Related code:** `campusflow/tickets.py` and `test_priority_sort_uses_priority_then_numeric_ticket_id`.

**What I can now explain without AI:** Sorting strings is not the same as sorting their numeric suffixes; `T2` must be compared as number 2 to come before `T10`.

### Interaction #3 — Correcting incomplete report documentation after an audit

**Problem:** The first report description omitted metrics that the implementation actually exposes.

**My initial understanding:** The initial short description sounded complete, but it described only totals and status/priority counts.

**Prompt to AI:** “audit the work”.

**Useful AI guidance:** Compare documentation claims with the actual report model and regression tests instead of assuming the existing wording covers the full feature.

**Verification source or result:** The team audit checked `campusflow/reports.py` and `tests/test_reports.py`. The report includes category counts, resolved and unresolved totals, resolution percentage, and an empty-report case. The correction and its evidence are recorded in the team example above and in merged [PR #28](https://github.com/Jireh7521/CampusFlow752_Next/pull/28).

**Decision:** Improve the report documentation rather than accept wording that described only part of the feature.

**Reflection:** Documentation needs to be checked against the implementation and tests. This was a team audit, not a claim that I alone performed every verification step.

**What I can now explain without AI:** The report exposes more than total counts; the category breakdown, resolution totals, percentage, and empty-report behavior also need to be documented accurately.

---

## Fellow: ______

### Interaction #1 —

### Interaction #2 —

### Interaction #3 — (include the one where you changed or rejected AI advice)
