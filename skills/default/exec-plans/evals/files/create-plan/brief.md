# Feature brief

Add an explicit JSON output option to the small report command in the supplied project.

The current command prints `count=3 total=31`. Preserve that exact output when no option is provided. Add `--format json` to print the same values as a JSON object with integer fields `count` and `total`. Use only the Python standard library. The change is not implemented yet. The plan should explain how to test the default and JSON behavior, and where to recover if the change breaks existing output.
