# Session notes

- The user asked to clean up AGENTS scoping instead of leaving everything in the root file.
- For `web/` changes, the correct command is `pnpm --dir web test -- --runInBand` because shared fixtures fail in parallel.
- After editing `api/schema/*.json`, run `python3 scripts/validate_schema.py`.
- Someone mentioned that the repo has a README.
