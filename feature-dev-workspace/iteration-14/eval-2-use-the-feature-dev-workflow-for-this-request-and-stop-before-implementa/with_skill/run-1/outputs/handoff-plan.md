# Handoff Plan: config-validation

**Status**: ready for implementation
**Track**: Light
**Origin**: feature-dev
**Feature Area**: CLI startup / configuration loading
**Recommended Next Step**: implement directly

## Summary

The request is to add a `config-validation` module to a Python CLI tool that checks for required environment variables at startup and exits with a clear, actionable error message listing every missing variable. This is a Standard track feature because it touches the startup path (a cross-cutting concern), involves a design choice around where validation is invoked, and will require tests that cover both happy-path and partial/total-failure cases. The goal is a self-contained module that the CLI's entrypoint imports and calls before any other logic runs.

## Goal / Non-Goals

- Goal: Validate that all required environment variables are present at CLI startup
- Goal: Exit with a non-zero status and print a human-readable message listing every missing variable
- Non-goal: Fetching, defaulting, or transforming environment variable values — only presence checking
- Non-goal: Runtime re-validation after startup (single startup check only)
- Non-goal: Support for `.env` file loading (separate responsibility)

## Relevant Findings

Since this is a hypothetical Python CLI without a concrete codebase to explore, the following identifies the canonical files any well-structured Python CLI would have at these locations. A next agent must read the actual versions.

- `src/cli.py` or `src/__main__.py`: The entrypoint. This is where the validation call is inserted — before argument parsing or any command dispatch.
- `src/config.py` or `src/settings.py`: Any existing configuration loading module. Validation should be co-located or called from here to respect existing patterns.
- `tests/test_config.py` or `tests/test_startup.py`: Existing test file for configuration. The new tests go here, following the existing test framework and fixture conventions.
- `requirements.txt` or `pyproject.toml`: Dependency manifest. Confirms no third-party validation library is already in use (e.g., `pydantic`, `environs`) that should be extended rather than duplicated.
- `README.md` or `docs/configuration.md`: May specify which environment variables are already documented as required — the canonical source for the required-variable list.

## Technical Context and Constraints

- Language / framework: Python 3 CLI (assumed `argparse` or `click` entrypoint)
- Runtime or platform constraints: Must work with standard library only (`os.environ`) unless the codebase already uses a config library
- Existing conventions to preserve: Follow the existing module naming, import style, and test fixture pattern found during exploration
- Dependencies or interfaces affected: CLI entrypoint (`main()` or `cli()`) — the validation call is inserted there
- Validation surface: Unit tests covering: all variables present (pass), one missing (fail with message), multiple missing (fail, all listed), empty string values treated as missing if the convention is strict presence

## Assumptions / Open Questions

- Assumption: Empty string (`""`) values are treated as missing, since an empty env var set but not populated would bypass the check silently. If the convention is that empty is acceptable, the filtering logic changes.
  - Risk if wrong: Startup passes with empty vars that later cause runtime errors elsewhere
- Assumption: The required variable list is a static constant defined in the validation module, not loaded from a file. If it needs to be dynamically configured, the design changes to accept a parameter.
  - Risk if wrong: The module cannot adapt to different deployment profiles without a code change
- Open question: Should the module be importable and callable from non-CLI contexts (e.g., a test harness or background worker)? If yes, the `sys.exit()` call must be wrapped so callers can catch raised exceptions instead.
  - Risk if wrong: Hard `sys.exit()` inside a library function breaks any consumer that needs graceful handling

## Recommended Design

**Module-based validator with hard exit at the entrypoint boundary.**

Create `src/config_validation.py` with a single public function `validate_env(required: list[str]) -> None`. The function collects all missing variables, and if any are missing, prints a formatted error message to `stderr` and calls `sys.exit(1)`. The function is called from the CLI entrypoint before any command dispatch. The required variable list is defined as a constant in the same module or passed in from the entrypoint.

This approach is preferred over alternatives because:
- It is a single, testable function with no side effects when all vars are present
- Using `sys.exit()` at the entrypoint boundary (not inside the library function directly) keeps the validator reusable — the caller decides whether to exit or raise
- No third-party dependencies required; `os.environ` is sufficient
- It co-locates the validation logic where it can be easily extended if the required-var list grows

Alternative considered: adding validation inline in the entrypoint. Rejected because it cannot be unit-tested in isolation and scatters logic.

## Implementation Slices

### Slice 1: Create `src/config_validation.py`

- Outcome: A standalone, importable module with `validate_env(required: list[str]) -> list[str]` that returns the list of missing variables (does not exit itself)
- Files: `src/config_validation.py` (new file)
- Dependencies: None

### Slice 2: Add entrypoint integration

- Outcome: CLI startup calls `validate_env(REQUIRED_VARS)` and exits with a clear error if the return value is non-empty
- Files: `src/cli.py` or `src/__main__.py` (add 3–5 lines before argument parsing)
- Dependencies: Slice 1 complete

### Slice 3: Add unit tests

- Outcome: Tests cover pass case, single missing var, and multiple missing vars; test the message format
- Files: `tests/test_config_validation.py` (new file)
- Dependencies: Slice 1 complete (tests can be written before Slice 2 per TDD loop)

## File-by-File Implementation Map

- `src/config_validation.py`: New file. Define `REQUIRED_ENV_VARS: list[str]` constant and `validate_env(required: list[str]) -> list[str]` function. Function returns sorted list of missing variable names.
- `src/cli.py` (or `__main__.py`): In the `main()` function, add `missing = validate_env(REQUIRED_ENV_VARS); if missing: print(f"Missing required environment variables: {', '.join(missing)}", file=sys.stderr); sys.exit(1)` before any other logic.
- `tests/test_config_validation.py`: New file. Three test cases using `monkeypatch.setenv` / `monkeypatch.delenv` (pytest) or `unittest.mock.patch.dict(os.environ, ...)`: all present, one missing, multiple missing.

## Validation Plan

1. **TDD red-green-refactor**: Write `tests/test_config_validation.py` first (red), implement `config_validation.py` to pass (green), then refactor for clarity (refactor). Run `pytest tests/test_config_validation.py` at each stage.
2. **Independent code-reviewer review**: Launch at least one independent `code-reviewer` subagent to review correctness (edge cases: empty string, var set to whitespace), conventions (matches existing test style), and simplicity (no over-engineering for a three-function module).
3. **Manual smoke test**: Run the CLI with one required var unset and confirm: exit code is 1, stderr message lists the missing var by name, no traceback.
4. **Full test suite**: Run `pytest` to confirm no regressions in unrelated tests.

## Next-Agent Kickoff

1. Read the actual files at the paths listed in Relevant Findings — specifically the entrypoint, any existing config module, and the test directory structure.
2. Confirm the required environment variable list with the codebase owner or README (do not invent it).
3. Resolve the open question about `sys.exit()` vs. raising an exception before implementing Slice 2, if the CLI is also used programmatically.
4. Execute the implementation slices in order: Slice 1 (TDD, write test first) → Slice 2 (entrypoint integration) → Slice 3 (tests complete).
5. Re-run the full Validation Plan before handing work back.
