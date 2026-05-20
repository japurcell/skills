PLAN:
1. Load repo rules (AGENTS.md, .github/copilot-instructions.md, ~/.copilot/copilot-instructions.md if present).
2. Read target files under the fixture repo: evals/files/plan-fixture/src/report_builder.py, evals/files/plan-fixture/src/report_serializer.py, evals/files/plan-fixture/tests/test_report_builder.py.
3. Run the test suite to record a failing/passing baseline.
4. Identify the exact identifier to rename (OldName -> NewName).
5. Edit the three files to rename the identifier and update imports/usages.
6. Run tests and linters; iterate until green.
7. Commit changes on a feature branch with a clear message.
