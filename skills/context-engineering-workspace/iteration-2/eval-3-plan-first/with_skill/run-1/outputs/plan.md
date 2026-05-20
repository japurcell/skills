PLAN:
1. Confirm rename target: change key 'display_name' to 'title'. If you prefer a different name, reply now to redirect.
2. Read target files and tests; make the edits across files: in src/report_builder.py return {"title": row["name"]}; in src/report_serializer.py read report["title"]; update tests/test_report_builder.py accordingly; run tests after each edit.
3. Run full test suite, fix failures, run linters/typing if present, and prepare a single commit/PR containing the cross-file rename.
Executing unless you redirect.
