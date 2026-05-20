PLAN:
1. Load rules: AGENTS.md, .github/copilot-instructions.md, ~/.copilot/copilot-instructions.md (if present).
2. Read the relevant spec/request and target files: src/report_builder.py, src/report_serializer.py, tests/test_report_builder.py.
3. Run the test suite to capture baseline failures.
4. Identify the symbol to rename and all definitions/usages across the three files.
5. Perform a safe cross-file rename (update definition, imports, and tests) using refactor tooling or precise edits.
6. Re-run tests and iterate until all tests pass.
7. Commit the changes with a descriptive message.
Executing unless you redirect.
