PLAN
- Inspect the fixture repo at evals/files/plan-fixture to identify the symbol(s) and all usages in:
  src/report_builder.py, src/report_serializer.py, tests/test_report_builder.py
- Perform an atomic cross-file rename: update the definition and all imports/usages across the three files.
- Run the test suite and iterate until tests pass; fix remaining references and imports as needed.
