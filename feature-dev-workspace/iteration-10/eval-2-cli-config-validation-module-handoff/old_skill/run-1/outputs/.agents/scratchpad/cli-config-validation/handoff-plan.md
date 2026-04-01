# Handoff Plan: CLI Config Validation Module

**Status**: ready for implementation
**Track**: Standard
**Origin**: feature-dev
**Feature Area**: startup / configuration
**Recommended Next Step**: implement directly

## Summary

Add a `config_validation` module to a Python CLI tool that checks for required environment variables at startup and exits immediately with a clear, human-readable error message listing every missing variable. The feature is Standard track: it is a new module, requires integration into the existing entry point, demands a TDD loop to drive correctness, a code-simplifier pass for elegance, and an independent code-reviewer pass for quality. Implementation should stop before the code-simplifier and reviewer phases so those can proceed in a follow-up turn.

## Goal / Non-Goals

- Goal: Implement `src/<pkg>/config/validation.py` with a `validate_env(required: list[str]) -> None` function that collects all missing vars and exits with a formatted error.
- Goal: Integrate the validation call into the CLI entry point before argument parsing begins.
- Goal: Provide a complete pytest test suite for the module, written test-first (TDD red-green-refactor).
- Non-goal: Dynamic or schema-based config (e.g., pydantic-settings, .env file loading) — this handles bare `os.environ` checks only.
- Non-goal: Warning-level validation or partial-startup behavior when env vars are absent.
- Non-goal: Validation of env var _values_, only presence.

## Relevant Findings

Since there is no real codebase to explore, the following are reasonable defaults for a standard Python CLI tool. The implementing agent should verify each before writing code.

- `src/<pkg>/__main__.py` or `src/<pkg>/cli.py`: likely entry point; the validation call belongs here, before `main()` executes any logic.
- `src/<pkg>/config/` (may not exist yet): target home for the new module; create `__init__.py` if absent.
- `tests/` or `tests/unit/`: existing test directory; new test file goes here.
- `pyproject.toml` or `setup.cfg`: check for any linting (ruff/flake8) or test configuration that constrains file placement.
- `requirements.txt` / `pyproject.toml [project.dependencies]`: no new runtime dependencies are needed; pytest is assumed available for tests.

## Technical Context and Constraints

- Language / framework: Python 3.9+ CLI tool; argparse, click, or typer assumed at entry point.
- Runtime or platform constraints: `os.environ` is the only env-var source; no dotenv loading.
- Existing conventions to preserve: follow the project's import style (relative vs absolute), naming conventions, and error-exit patterns (if the project already calls `sys.exit` with a specific format, mirror it).
- Dependencies or interfaces affected: only the entry-point module that calls `main()` or the CLI group; no other callers anticipated.
- Validation surface: `pytest` test suite; linting via ruff or flake8 if present.

## Assumptions / Open Questions

- Assumption: The tool uses `os.environ` directly (or an equivalent dict-like mapping) rather than a managed config layer.
  - Risk if wrong: The integration point changes; the function signature may need a `env: Mapping[str, str] = os.environ` parameter regardless (recommended for testability).
- Assumption: The exit code for a missing-variable failure is `1`.
  - Risk if wrong: Minor; exit code is a one-line change.
- Assumption: The required variable list is known at import time (i.e., it can be declared as a module-level constant in the entry point).
  - Risk if wrong: If the list is dynamic, the validate call moves inside a function; the module itself is unchanged.
- Open question: Does the project already have a `config/` sub-package? If not, the implementing agent must create `src/<pkg>/config/__init__.py`.

## Recommended Design

**Single-responsibility validation function with an injected env mapping.**

```python
# src/<pkg>/config/validation.py
import os
import sys
from collections.abc import Mapping


def validate_env(
    required: list[str],
    env: Mapping[str, str] | None = None,
) -> None:
    """Exit with a clear error if any required env var is absent."""
    if env is None:
        env = os.environ
    missing = [var for var in required if var not in env]
    if missing:
        lines = ["Missing required environment variables:"] + [
            f"  - {var}" for var in missing
        ]
        print("\n".join(lines), file=sys.stderr)
        sys.exit(1)
```

Injecting `env` as a parameter keeps `os.environ` out of the function body, making the function trivially testable without monkeypatching. This fits the codebase better than a class-based solution because the feature is purely functional (check presence, exit or continue).

**Entry point integration** (in `cli.py` or `__main__.py`):

```python
from <pkg>.config.validation import validate_env

REQUIRED_ENV_VARS = [
    "DATABASE_URL",
    "SECRET_KEY",
    # ... project-specific list
]

def main() -> None:
    validate_env(REQUIRED_ENV_VARS)
    # ... rest of startup
```

The constant `REQUIRED_ENV_VARS` lives in the entry point rather than in `validation.py` so the validation module stays generic and reusable.

## Implementation Slices

### Slice 1: TDD — core validation module

- Outcome: `validate_env` is fully tested and passing; the module exists and is importable.
- Files:
  - `tests/unit/test_config_validation.py` (write first, red; then green)
  - `src/<pkg>/config/__init__.py` (create if absent)
  - `src/<pkg>/config/validation.py`
- Dependencies: none; this slice is standalone.

**Red-green-refactor loop for Slice 1:**

1. **Red** — write failing tests:

   ```python
   # tests/unit/test_config_validation.py
   import pytest, sys
   from <pkg>.config.validation import validate_env

   def test_passes_when_all_vars_present():
       validate_env(["FOO", "BAR"], env={"FOO": "1", "BAR": "2"})  # no exception

   def test_exits_1_when_var_missing(capsys):
       with pytest.raises(SystemExit) as exc_info:
           validate_env(["FOO", "MISSING"], env={"FOO": "1"})
       assert exc_info.value.code == 1

   def test_lists_all_missing_vars(capsys):
       with pytest.raises(SystemExit):
           validate_env(["A", "B", "C"], env={})
       captured = capsys.readouterr()
       assert "A" in captured.err
       assert "B" in captured.err
       assert "C" in captured.err

   def test_error_message_labels_missing_vars(capsys):
       with pytest.raises(SystemExit):
           validate_env(["SECRET_KEY"], env={})
       captured = capsys.readouterr()
       assert "Missing required environment variables" in captured.err
       assert "SECRET_KEY" in captured.err

   def test_passes_with_empty_required_list():
       validate_env([], env={})  # no exception
   ```

   Run `pytest` → all tests fail (module does not exist yet).

2. **Green** — implement the minimal `validate_env` shown in Recommended Design. Run `pytest` → all pass.

3. **Refactor** — review for clarity; no logic changes expected at this stage.

### Slice 2: Integration — entry point wiring

- Outcome: The CLI calls `validate_env` at startup; end-to-end smoke test passes.
- Files:
  - `src/<pkg>/cli.py` or `src/<pkg>/__main__.py` (add import and call)
  - `tests/integration/test_cli_startup.py` (optional end-to-end test using `subprocess` or `CliRunner`)
- Dependencies: Slice 1 complete.

### Slice 3: Code-simplifier refactor pass

- Outcome: The module and its test file are reviewed for elegance, redundancy, and readability by the code-simplifier skill.
- Files: `src/<pkg>/config/validation.py`, `tests/unit/test_config_validation.py`
- Dependencies: Slice 2 complete.
- Instructions for implementing agent: invoke the `code-simplifier` skill on the two files listed above. Do not change behavior; only improve clarity and reduce noise.

### Slice 4: Independent code-reviewer review

- Outcome: A `code-reviewer` agent has reviewed the feature end-to-end for correctness, security, conventions, and test coverage.
- Files: all files touched in Slices 1–3.
- Dependencies: Slice 3 complete.
- Instructions for implementing agent: launch an independent `code-reviewer` agent with focuses: (a) correctness and edge cases (empty list, env var present but empty string), (b) security (ensure no sensitive values are leaked in error output), (c) test coverage gaps.

## File-by-File Implementation Map

- `src/<pkg>/config/__init__.py`: create empty file if the `config` sub-package does not yet exist.
- `src/<pkg>/config/validation.py`: new file with `validate_env(required, env)` as specified above.
- `src/<pkg>/cli.py` (or `__main__.py`): add `from <pkg>.config.validation import validate_env`; add `REQUIRED_ENV_VARS` constant; call `validate_env(REQUIRED_ENV_VARS)` at the top of `main()`.
- `tests/unit/test_config_validation.py`: new file with the five test cases from Slice 1 (red phase).

## Validation Plan

- **Automated**:
  - `pytest tests/unit/test_config_validation.py -v` → all 5 tests pass.
  - `pytest` (full suite) → no regressions.
  - Linter: `ruff check src/<pkg>/config/validation.py` (or project equivalent) → no errors.
- **Manual**:
  - Run the CLI without a required var set: `SECRET_KEY="" python -m <pkg>` → stderr shows "Missing required environment variables: / - SECRET_KEY"; process exits 1.
  - Run CLI with all vars set → normal startup, no error output.
- **Review focus (for code-reviewer agent)**:
  - Does `validate_env` leak env var _values_ in the error message? (It should not.)
  - Are env vars that are set to empty string (`""`) treated as present or missing? (Current design: present. Confirm this is correct for the project. If empty-string vars should also be treated as missing, add `or not env[var]` to the comprehension.)
  - Is the import of `validate_env` placed before any other side-effectful imports in the entry point?

## Next-Agent Kickoff

1. Read `src/<pkg>/cli.py` (or `__main__.py`) to confirm the entry point pattern and import style.
2. Read `pyproject.toml` or `setup.cfg` to confirm test directory, linting rules, and any existing config sub-package.
3. If `src/<pkg>/config/` does not exist, create `src/<pkg>/config/__init__.py` first.
4. Follow the TDD loop in Slice 1 exactly: write all tests first, confirm they fail, then implement `validate_env`, confirm they pass.
5. Wire the integration in Slice 2.
6. Invoke the `code-simplifier` skill on the two files from Slice 3.
7. Launch an independent `code-reviewer` agent for Slice 4 with the three focuses listed in the Validation Plan.
8. Re-run `pytest` (full suite) after each slice before advancing.
9. Do not change `REQUIRED_ENV_VARS` without confirming with the user — this list is project-specific.
