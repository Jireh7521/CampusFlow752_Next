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

## Fellow: ______

### Interaction #1 —

### Interaction #2 —

### Interaction #3 — (include the one where you changed or rejected AI advice)

---

## Fellow: ______

### Interaction #1 —

### Interaction #2 —

### Interaction #3 — (include the one where you changed or rejected AI advice)
