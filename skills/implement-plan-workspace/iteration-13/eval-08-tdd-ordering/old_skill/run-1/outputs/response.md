## Phase Execution

Phase Handoff: Core
- Sequential tasks:
  1. `T007` — write API endpoint tests in `tests/api_test.py`
  2. `T008` — implement API endpoint in `src/api/routes.py`

Ordering rule applied
- `T007` runs before `T008` because test tasks execute before their implementation counterparts inside the same phase.
- `T007` is verified first with a RED test run. A clean RED is acceptable because it proves the test is targeting behavior that does not exist yet.
- Only after `T007` is verified does `T008` begin.
- `T008` is marked `[X]` only after the related build/lint checks and test run pass.
