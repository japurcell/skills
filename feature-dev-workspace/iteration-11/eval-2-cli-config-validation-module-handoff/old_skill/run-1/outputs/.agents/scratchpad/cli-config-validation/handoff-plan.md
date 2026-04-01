# Handoff Plan: cli-config-validation

**Status**: ready for implementation
**Track**: Standard
**Origin**: feature-dev
**Feature Area**: startup / bootstrap
**Recommended Next Step**: implement directly

## Summary

The request is to add a configuration-validation module to an existing Python CLI tool. The module must run at startup, inspect the environment for a declared set of required variables, and exit immediately with a clear, actionable error message that lists every missing variable if any are absent. No existing codebase was provided, so this plan is written for a conventional Python CLI project (Click or argparse entry-point, src-layout or flat layout, `pyproject.toml` or `setup.cfg`). The standard track was chosen because the feature touches the entry-point, adds a new module, and has one non-trivial design choice around where validation is invoked.

## Goal / Non-Goals

- Goal: Provide a `config_validator` module that checks for required env vars and exits with a clear error listing all missing ones.
- Goal: Integrate the validator so it runs automatically at CLI startup before any command logic executes.
- Goal: Keep the module independently testable without actually running the CLI.
- Non-goal: Secret management, `.env` file loading, or value-format validation (type coercion, regex checks).
- Non-goal: Providing default values or fallbacks for missing variables.

## Relevant Findings

- `src/<package>/cli.py` (or `__main__.py`): the CLI entry-point where the validator must be invoked; pattern assumed to use Click's `@click.group()` or a top-level `main()` guarded by `if __name__ == "__main__"`.
- `src/<package>/config.py` (if present): likely home for env-var names as constants; new `REQUIRED_ENV_VARS` list should live here or in the new module.
- `tests/`: existing test suite location; new `tests/test_config_validator.py` must be added alongside it.
- `pyproject.toml` / `setup.cfg`: no new runtime dependencies are needed (stdlib `os` only).

> Because no real codebase was supplied, the file paths above are conventional placeholders. The implementing agent must verify them before writing code.

## Technical Context and Constraints

- Language / framework: Python 3.9+ (assume `os.environ`, no third-party env libs needed); CLI framework likely Click or argparse.
- Runtime or platform constraints: Must work in any POSIX/Windows environment; `sys.exit(1)` is the correct exit mechanism for CLI tools.
- Existing conventions to preserve: Follow the project's module naming style; import the validator in `cli.py` before any command registration so it fires on every invocation.
- Dependencies or interfaces affected: `cli.py` entry-point gains one import and one call; nothing else changes.
- Validation surface: `pytest` unit tests for the validator; no new integration test harness required.

## Assumptions / Open Questions

- Assumption: The list of required env vars will be defined as a module-level constant in `config_validator.py` (e.g., `REQUIRED: list[str]`). If the project already has a central config constants file, move the list there and import it.
- Assumption: The validator runs unconditionally on every CLI invocation (including `--help`). If this is undesirable, the implementing agent should gate it behind a flag or run only for non-help invocations.
- Assumption: Exit code `1` is the correct failure code. If the project defines a dedicated exit-code registry, use the appropriate constant.
- Open question: Should the error message be written to `stderr` only, or also logged via a logger? (Minor; default to `stderr`.)
- Risk if wrong (startup-gate assumption): If validation fires during `--help`, it may confuse users who need to read usage without having credentials set. Mitigate by checking `sys.argv` for `--help` if needed.

## Recommended Design

**Single validate-and-exit function in a dedicated `config_validator.py` module**, called once at the top of `cli.py` before any command is registered or invoked.

This is preferred over the main alternative (raising a custom exception and catching it in `main()`) because:

- A single `sys.exit` call at the point of failure produces a cleaner stack trace.
- The module remains independently callable and testable — just import `validate_env` and call it with a mock environment.
- It avoids adding an exception type to the public API surface, keeping the module's contract simple.

## Implementation Slices

### Slice 1: Create `config_validator.py`

- Outcome: A standalone module exists with a `validate_env(required, env=None)` function; passing `None` for `env` defaults to `os.environ`; calling it with missing vars prints a formatted error to `stderr` and calls `sys.exit(1)`; calling it with all vars present returns normally.
- Files: `src/<package>/config_validator.py`
- Dependencies: stdlib only (`os`, `sys`).

### Slice 2: Define required-var list

- Outcome: `REQUIRED_ENV_VARS: list[str]` constant is declared (either inside `config_validator.py` or in an existing config constants module).
- Files: `src/<package>/config_validator.py` (or `src/<package>/config.py` if it exists)
- Dependencies: Slice 1 complete.

### Slice 3: Wire into CLI entry-point

- Outcome: `cli.py` (or `__main__.py`) imports `validate_env` and `REQUIRED_ENV_VARS` and calls `validate_env(REQUIRED_ENV_VARS)` as the first statement in `main()` / before the `click.group` is invoked.
- Files: `src/<package>/cli.py`
- Dependencies: Slices 1 and 2 complete.

### Slice 4: Tests

- Outcome: `tests/test_config_validator.py` covers: all vars present (passes), one var missing (exits 1, message contains var name), multiple vars missing (exits 1, message lists all), empty required list (passes).
- Files: `tests/test_config_validator.py`
- Dependencies: Slice 1 complete.

## File-by-File Implementation Map

- `src/<package>/config_validator.py`: New file. Implement `validate_env(required: list[str], env: dict | None = None) -> None`. Collect missing = [v for v in required if v not in env]. If missing, print `f"Error: the following required environment variables are not set:\n  " + "\n  ".join(missing)` to `sys.stderr`, then `sys.exit(1)`.
- `src/<package>/config.py` (if exists): Add `REQUIRED_ENV_VARS: list[str] = [...]` with the project's actual variable names, or keep in `config_validator.py` if no config module exists.
- `src/<package>/cli.py`: Add `from <package>.config_validator import validate_env, REQUIRED_ENV_VARS` near top; add `validate_env(REQUIRED_ENV_VARS)` as first call inside `main()` or equivalent entry function.
- `tests/test_config_validator.py`: New file. Use `pytest` with `monkeypatch.setenv` / `monkeypatch.delenv` and `pytest.raises(SystemExit)` to assert exit code and message content.

## Validation Plan

- Automated: `pytest tests/test_config_validator.py -v` — all four cases must pass.
- Automated: Run existing test suite to confirm no regressions.
- Manual: `unset MY_REQUIRED_VAR && python -m <package> <subcommand>` — should exit with code 1 and print all missing var names.
- Manual: With all vars set, `python -m <package> --help` — should display usage normally.
- Review focus: Ensure `sys.exit` is not swallowed by any outer exception handler in `cli.py`; confirm the error message lists _all_ missing vars, not just the first one.

## Next-Agent Kickoff

1. Identify the real entry-point file (check `pyproject.toml` `[project.scripts]` or `setup.cfg` `[options.entry_points]`) and replace placeholder paths above.
2. Execute Slices 1–4 in order.
3. If an existing `config.py` or `settings.py` is found, move `REQUIRED_ENV_VARS` there and update the import in `cli.py` and tests accordingly.
4. Stop and ask if the open question about `--help` gating is blocking (it likely is not for a first implementation).
5. Run the Validation Plan before handing work back.
