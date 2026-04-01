# Handoff Plan: cli-config-validation

**Status**: ready for implementation
**Track**: Standard
**Origin**: feature-dev
**Feature Area**: CLI startup / configuration layer
**Recommended Next Step**: implement directly — all decisions resolved, no blocking questions remain

## Summary

The request is to add a configuration-validation module to a Python CLI tool that checks for required environment variables at startup and exits with a clear, descriptive error message listing every missing variable. Chosen track is Standard: the change is bounded (one new module + one entrypoint integration), but it introduces a new public interface contract, requires deliberate error-formatting choices, and must be covered by a complete TDD loop with a code-simplifier refactor pass and an independent code-reviewer pass. Implementation is not started here; this plan provides everything a receiving agent needs to proceed.

## Goal / Non-Goals

- **Goal**: Implement `validate_env()` in a dedicated `config.py` module that accepts a list of required variable names, detects every missing one in a single pass, and calls `sys.exit(1)` with a formatted message listing them all.
- **Goal**: Integrate `validate_env()` into the CLI entrypoint so validation runs before any command logic executes.
- **Goal**: Achieve 100 % branch coverage on the validation module via TDD.
- **Non-goal**: Loading or parsing variable values (type casting, validation of variable _content_).
- **Non-goal**: Support for `.env` file loading (that is a separate concern; the module consumes `os.environ` as-is).
- **Non-goal**: Interactive prompting or auto-fixing missing variables.

## Relevant Findings

Since this is a greenfield module in an unspecified Python CLI project, the following assumptions represent the conventional structure of a standard Python CLI package. A receiving agent should verify these paths before writing code.

- `src/<package>/cli.py` (or `<package>/__main__.py`): CLI entrypoint — this is where `validate_env()` must be called first, before argument parsing or any business logic.
- `src/<package>/config.py` (NEW): home for `validate_env()`. Does not exist yet; must be created.
- `tests/test_config.py` (NEW): unit-test file for `config.py`; must be created first (TDD: write the test before the implementation).
- `pyproject.toml` / `setup.cfg` / `setup.py`: records project metadata and test dependencies; verify `pytest` is already listed.
- `requirements.txt` or equivalent: confirm no new runtime dependency is needed (stdlib `os` and `sys` only).

## Technical Context and Constraints

- **Language / framework**: Python 3.9+; `os.environ`, `sys.exit` (stdlib only — no new runtime dependencies).
- **Runtime constraint**: Validation must run synchronously before the CLI's command-dispatch loop. It must never be behind a flag or deferred.
- **Exit convention**: Non-zero exit code on failure. Use `sys.exit(1)` with a message written to `stderr`.
- **Error message format**: Human-readable, actionable. Example:
  ```
  Error: the following required environment variables are missing:
    - DATABASE_URL
    - SECRET_KEY
  Set them before running this tool.
  ```
- **Existing conventions to preserve**: Follow existing import style, type-annotation patterns, and module docstring format found in the codebase.
- **Validation surface**: `pytest` with `monkeypatch` for environment variable manipulation; no subprocess harness needed for unit tests.

## Assumptions / Open Questions

- **Assumption**: The list of required variable names is hardcoded as a constant in `config.py` (e.g., `REQUIRED_ENV_VARS: list[str] = [...]`). If the list needs to be dynamic or configurable via a file, the design changes slightly — a receiving agent should confirm if that is needed.
  - _Risk if wrong_: Minor; refactor to accept a parameter or read from a config file.
- **Assumption**: `pytest` is already in the dev-dependency set.
  - _Risk if wrong_: Add `pytest` to dev dependencies before running tests.
- **Assumption**: No existing `config.py` file conflicts with this path.
  - _Risk if wrong_: Choose a different module name (e.g., `env_check.py`) and adjust all references.
- **Assumption**: The project uses `src/` layout. If it is a flat layout, adjust all paths accordingly.

## Recommended Design

**Single-function module with hardcoded constant** — `validate_env(required: list[str] | None = None) -> None`. When called with no arguments it uses the module-level `REQUIRED_ENV_VARS` constant; callers can also inject a list for testability. This avoids a global side-effect-on-import anti-pattern while keeping the call site in `cli.py` minimal (`validate_env()`).

Chosen over _raise-an-exception_ design because: CLI tools conventionally use `sys.exit` at boundaries rather than propagating exceptions; it keeps error presentation consistent with other CLI error paths; and it avoids littering `try/except SystemExit` in tests.

## Implementation Slices

### Slice 1: Write failing tests (red)

- **Outcome**: `tests/test_config.py` exists with at least three test cases — (a) all variables present → no exit, (b) one variable missing → `sys.exit(1)` with the variable name in the message, (c) multiple variables missing → exit lists all of them.
- **Files**: `tests/test_config.py`
- **Dependencies**: `pytest` available; `config.py` does not yet exist (tests will fail with `ImportError` — that is the red state).

### Slice 2: Implement `config.py` (green)

- **Outcome**: All tests in `tests/test_config.py` pass.
- **Files**: `src/<package>/config.py`
- **Dependencies**: Slice 1 complete.

### Slice 3: Integrate into CLI entrypoint

- **Outcome**: `validate_env()` is called at the top of the CLI entrypoint before any other logic. Manual smoke test confirms the CLI exits with a clear message when a required variable is unset.
- **Files**: `src/<package>/cli.py` (or `__main__.py`)
- **Dependencies**: Slice 2 complete.

### Slice 4: code-simplifier refactor pass (refactor)

- **Outcome**: An independent code-simplifier agent reviews `config.py` and the test file for redundancy, clarity, and idiom quality. Any agreed changes are applied. Tests still pass after refactor.
- **Files**: `src/<package>/config.py`, `tests/test_config.py`
- **Dependencies**: Slice 3 complete, all tests green.

### Slice 5: independent code-reviewer pass

- **Outcome**: An independent code-reviewer agent reviews the full changeset for correctness, edge cases, security surface, and convention alignment. Findings are triaged; high-severity issues are fixed before marking done.
- **Files**: `src/<package>/config.py`, `tests/test_config.py`, `src/<package>/cli.py`
- **Dependencies**: Slice 4 complete.

## File-by-File Implementation Map

- `tests/test_config.py` (**CREATE**): Three pytest test functions using `monkeypatch.setenv` / `monkeypatch.delenv` to control environment state. Use `pytest.raises(SystemExit)` (or `capsys` + `monkeypatch`) to assert on exit code and stderr output. Write this file _first_.
- `src/<package>/config.py` (**CREATE**): Module with `REQUIRED_ENV_VARS: list[str]` constant and `validate_env(required: list[str] | None = None) -> None`. Body: collect missing vars in one pass, print message to `stderr`, call `sys.exit(1)` if any are missing.
- `src/<package>/cli.py` (**MODIFY**): Add `from <package>.config import validate_env` import and a `validate_env()` call as the first statement in the CLI entry function (before `argparse.parse_args()` or `@click.command` handler body).

## Validation Plan

### TDD Loop (red → green → refactor)

1. **Red**: Run `pytest tests/test_config.py` → expect `ImportError` (module not yet created). Confirm all three test functions are collected.
2. **Green**: Create `src/<package>/config.py` with minimal passing implementation. Run `pytest tests/test_config.py` → all pass.
3. **Coverage check**: Run `pytest --cov=src/<package>/config --cov-report=term-missing` → confirm 100 % coverage with no uncovered branches.
4. **Refactor** (Slice 4): Apply code-simplifier changes, re-run pytest → still green.

### Integration Smoke Test

```bash
# Unset a required variable and run the CLI
unset DATABASE_URL
python -m <package>
# Expected: exits with code 1, stderr lists DATABASE_URL as missing
echo $?   # → 1
```

### Automated

- `pytest tests/test_config.py -v` — all assertions pass
- `pytest --cov=src/<package>/config --cov-report=term-missing` — 100 % coverage
- `mypy src/<package>/config.py` (if mypy is configured) — no type errors
- `ruff check src/<package>/config.py` / `flake8` — no lint violations

### Review Focus (for code-reviewer agent)

- Edge cases: empty `required` list, duplicate entries, whitespace-only variable names.
- Error message content: verify all missing names appear; verify message goes to `stderr` not `stdout`.
- Exit code: confirm `sys.exit(1)` not `sys.exit(0)`.
- No global side effects on import (validation should only run when `validate_env()` is explicitly called).
- Thread safety is not required (CLI startup is single-threaded), but note the assumption.

## Next-Agent Kickoff

1. Read `src/<package>/cli.py` and `pyproject.toml` to confirm the entrypoint path and test runner configuration.
2. Confirm `pytest` is a dev dependency; add it if missing.
3. Execute Slice 1 first — write `tests/test_config.py` before creating `config.py`.
4. Run `pytest tests/test_config.py` and confirm the red state (ImportError or NameError).
5. Implement `src/<package>/config.py` (Slice 2) until tests are green.
6. Integrate into `cli.py` (Slice 3) and run the smoke test.
7. Launch a `code-simplifier` subagent on `config.py` + `tests/test_config.py` (Slice 4).
8. Launch an independent `code-reviewer` subagent on the full changeset (Slice 5); fix any high-severity findings.
9. Re-run the full validation plan before declaring the feature complete.
10. Stop and ask for clarification only if the `REQUIRED_ENV_VARS` list needs to be dynamic (see Assumptions) or if a conflicting `config.py` already exists.
