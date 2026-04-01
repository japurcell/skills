# Handoff Plan: CLI Config Validation Module

**Status**: ready for implementation
**Track**: Standard
**Origin**: feature-dev
**Feature Area**: Startup / configuration
**Recommended Next Step**: implement directly — all blocking questions resolved via stated assumptions; no codebase exploration was possible (no target repo provided), so assumptions are explicit below

---

## Summary

A Python CLI tool needs a dedicated configuration-validation module that runs at startup, checks that all required environment variables are present, and exits immediately with a clear, human-readable error message that lists every missing variable if any are absent. The work is Standard-track: it touches the entry point, introduces a new module, and needs tests, but has no cross-cutting dependencies or ambiguous product requirements. This handoff captures the design, implementation map, and validation plan so a follow-on agent can implement without repeating discovery.

---

## Goal / Non-Goals

- **Goal**: Implement `config_validator.py` (or equivalent) that collects all missing required env vars and exits with a formatted error message naming each one.
- **Goal**: Wire `validate_config()` into the CLI entry point so it runs before any other work.
- **Goal**: Ship unit tests for the validator covering: all vars present, some missing, all missing.
- **Non-goal**: Loading or coercing env var values (type conversion, defaults) — that is config-loading, not validation.
- **Non-goal**: Validating the _content_ of env vars (format, range) — only presence is required.
- **Non-goal**: Support for config files, `.env` files, or third-party libraries.

---

## Relevant Findings

> No target repository was provided. The findings below assume a conventional Python CLI project layout. The implementing agent should adjust paths if the actual layout differs.

- `src/<pkg>/cli.py` (or `<pkg>/main.py`): CLI entry point — `main()` / `cli()` is where `validate_config()` must be called first.
- `src/<pkg>/config.py` (or `<pkg>/settings.py`): If this file exists it may already hold env-var reads; `validate_config()` can either live here or in a sibling module — keep it separate if `config.py` already has other concerns.
- `tests/test_cli.py` (or `tests/test_main.py`): Existing CLI tests — add a `test_config_validator.py` alongside.
- `pyproject.toml` / `setup.cfg` / `requirements.txt`: Confirm no third-party config library (e.g. `pydantic-settings`, `dynaconf`) is already in use; if one is, prefer extending it over adding a custom module.

---

## Technical Context and Constraints

- **Language / framework**: Python 3.8+; stdlib only (`os`, `sys`). No new dependencies.
- **Runtime**: CLI invoked as a script or via an entry-point declared in `pyproject.toml`. Validation must fire before argument parsing or any I/O.
- **Existing conventions to preserve**: Follow the project's existing import style, module naming, and test layout.
- **Exit behavior**: Use `sys.exit(1)` — exit code 1 is the standard for configuration/usage errors. Do **not** raise an unhandled exception; the error should be user-readable, not a traceback.
- **Error message format**: List every missing variable, not just the first. Human-readable, actionable.
- **Validation surface**: Pure-unit-testable — monkeypatch `os.environ` to simulate missing/present vars.

---

## Assumptions / Open Questions

- **Assumption**: The project does not already use a config-management library that handles required-var validation. If it does, extend that library's validation surface instead.
  - _Risk if wrong_: Duplication; two validation paths could diverge silently.
- **Assumption**: The set of required env vars is known at module import time (a static list), not derived from runtime state.
  - _Risk if wrong_: The `REQUIRED_ENV_VARS` constant approach won't work; would need a factory or callable.
- **Assumption**: Exit code 1 is acceptable for missing-config errors (no project-specific exit-code convention).
  - _Risk if wrong_: Minor; easy to adjust the constant.
- **Assumption**: The CLI entry point is a single `main()` (or `cli()`) function. If there are multiple subcommand entry points, each needs the validation call or it moves to a shared initializer.
- **Open question** (non-blocking): Should the required-var list be defined in `config_validator.py` itself, or injected by the caller? Recommendation: define it in `config_validator.py` as a module-level constant for simplicity; callers can override via the `required` parameter if needed (see design below).

---

## Recommended Design

**Single-module validator with an explicit `required` parameter (optional override)**

Create `src/<pkg>/config_validator.py` with:

1. `REQUIRED_ENV_VARS: list[str]` — module-level constant listing every required variable name.
2. `validate_config(required: list[str] | None = None) -> None` — accepts an optional override list so callers can extend or replace the default for testing or dynamic use cases. Internally collects missing vars and calls `sys.exit(1)` with a structured message.

**Why this over alternatives**:

- _Inline in `main.py`_: harder to test in isolation; pollutes the entry point.
- _Extend `config.py`_: only preferred if `config.py` is already the canonical home for env-var access; creates coupling otherwise.
- _`pydantic-settings` or similar_: introduces a dependency and is overkill for a presence-only check.

The parameterised-`required` design future-proofs testing without complicating the happy path — callers invoke `validate_config()` with no args; tests pass a custom list.

---

## Implementation Slices

### Slice 1: Create `config_validator.py`

- **Outcome**: Standalone module that, when called, collects all missing required env vars and exits with a formatted error.
- **Files**: `src/<pkg>/config_validator.py` (new file)
- **Dependencies**: none

### Slice 2: Wire into CLI entry point

- **Outcome**: `validate_config()` is the first call inside `main()` / `cli()`; any missing-var run exits before doing any real work.
- **Files**: `src/<pkg>/cli.py` (or `main.py`) — add import and one function call
- **Dependencies**: Slice 1 complete

### Slice 3: Tests

- **Outcome**: `tests/test_config_validator.py` with ≥ 3 test cases; all pass.
- **Files**: `tests/test_config_validator.py` (new file)
- **Dependencies**: Slice 1 complete (Slice 2 not required for unit tests)

---

## File-by-File Implementation Map

### `src/<pkg>/config_validator.py` (create)

```python
"""Startup validation: ensure all required environment variables are present."""
from __future__ import annotations

import os
import sys

REQUIRED_ENV_VARS: list[str] = [
    # Populate with actual required variable names, e.g.:
    # "DATABASE_URL",
    # "SECRET_KEY",
    # "API_TOKEN",
]


def validate_config(required: list[str] | None = None) -> None:
    """Exit with a clear error if any required env vars are missing.

    Args:
        required: Override the default REQUIRED_ENV_VARS list. Primarily
                  useful in tests. Pass None to use the module default.
    """
    vars_to_check = required if required is not None else REQUIRED_ENV_VARS
    missing = [var for var in vars_to_check if not os.environ.get(var)]

    if missing:
        lines = ["Missing required environment variables:"]
        lines.extend(f"  - {var}" for var in missing)
        lines.append("Please set them before running.")
        sys.exit("\n".join(lines))
```

Key points:

- `os.environ.get(var)` returns `None` for absent vars _and_ treats empty-string values as missing (falsy). If empty-string should be allowed, use `var not in os.environ` instead — note the assumption and align with project conventions.
- `sys.exit(str)` writes to stderr and exits with code 1.

### `src/<pkg>/cli.py` (edit — add 2 lines)

```python
# At the top of the file, add the import:
from <pkg>.config_validator import validate_config

# As the first statement inside main() / cli():
def main() -> None:
    validate_config()          # <-- add this line
    # ... rest of existing main body unchanged
```

### `tests/test_config_validator.py` (create)

```python
"""Unit tests for config_validator.validate_config."""
import pytest
from <pkg>.config_validator import validate_config


def test_all_present_passes(monkeypatch):
    monkeypatch.setenv("APP_KEY", "value")
    monkeypatch.setenv("DB_URL", "postgres://localhost/db")
    # Should not exit
    validate_config(required=["APP_KEY", "DB_URL"])


def test_missing_one_exits(monkeypatch):
    monkeypatch.setenv("APP_KEY", "value")
    monkeypatch.delenv("DB_URL", raising=False)
    with pytest.raises(SystemExit) as exc_info:
        validate_config(required=["APP_KEY", "DB_URL"])
    assert "DB_URL" in str(exc_info.value)
    assert "Missing required environment variables" in str(exc_info.value)


def test_missing_multiple_lists_all(monkeypatch):
    monkeypatch.delenv("APP_KEY", raising=False)
    monkeypatch.delenv("DB_URL", raising=False)
    with pytest.raises(SystemExit) as exc_info:
        validate_config(required=["APP_KEY", "DB_URL"])
    msg = str(exc_info.value)
    assert "APP_KEY" in msg
    assert "DB_URL" in msg


def test_empty_required_list_passes():
    # No vars required — should never exit
    validate_config(required=[])
```

---

## Validation Plan

- **Automated**:
  - `pytest tests/test_config_validator.py -v` — all four tests must pass.
  - `python -m <pkg>` (or the declared entry point) with no env vars set — must print the missing-vars error and exit 1.
  - `python -m <pkg>` with all required vars set — must proceed normally (no spurious exit).
- **Manual**:
  - Run `unset ALL_REQUIRED_VARS && python -m <pkg>` — verify error message lists every missing var, not just the first.
  - Run `export ALL_REQUIRED_VARS=values && python -m <pkg>` — verify normal startup.
- **Review focus**:
  - Empty-string handling: confirm whether `os.environ.get(var)` (falsy) vs `var not in os.environ` (strict absence) matches project intent.
  - Call site in `cli.py`: confirm `validate_config()` fires before any I/O, logging, or argument parsing.
  - `sys.exit` message encoding: on some platforms `sys.exit(str)` writes to stderr without a newline; verify visibility in the terminal.

---

## Next-Agent Kickoff

1. Read `src/<pkg>/cli.py` (or `main.py`) to confirm the entry-point function name and existing import style before editing.
2. Read `src/<pkg>/config.py` or `settings.py` if it exists — if it already validates env vars in any form, consolidate rather than duplicate.
3. Check `pyproject.toml` / `setup.cfg` for any existing config-management dependency (pydantic-settings, dynaconf, etc.); if present, follow its validation pattern instead.
4. Populate `REQUIRED_ENV_VARS` with the actual variable names for this project.
5. Implement Slice 1 → Slice 2 → Slice 3 in order.
6. Run the Validation Plan before handing work back.
7. If the empty-string assumption (see Relevant Findings) is wrong, switch `os.environ.get(var)` to `var not in os.environ` and update the tests accordingly.
