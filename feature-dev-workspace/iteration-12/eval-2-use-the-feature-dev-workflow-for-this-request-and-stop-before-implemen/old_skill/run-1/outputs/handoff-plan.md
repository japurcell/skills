# Handoff Plan: Configuration Validation Module for Python CLI Startup

**Status**: ready for implementation
**Track**: Standard
**Origin**: feature-dev
**Feature Area**: CLI startup and configuration validation
**Recommended Next Step**: implement directly

## Summary

Prepare a startup-time configuration validation capability for a Python CLI tool so required environment variables are checked before command execution. If any required variables are missing, the CLI should exit non-zero and print a clear, user-readable error listing all missing variable names. This handoff stops before implementation and gives a concrete path another agent can execute.

## Goal / Non-Goals

- Goal: Add a dedicated configuration-validation module that validates required environment variables at process startup.
- Goal: Ensure failures are explicit, actionable, and deterministic (sorted missing variable list, stable message format).
- Non-goal: Introduce external config services, secret managers, or dynamic runtime discovery of required variables.
- Non-goal: Redesign the CLI command structure beyond inserting startup validation.

## Relevant Findings

- src/cli.py (or src/main.py): expected entrypoint where startup checks should run before command dispatch.
- src/config.py (or existing settings module): likely existing home for env-related constants and parsing patterns.
- tests/test_cli_startup.py (or equivalent): best place for process-exit and stderr assertion coverage.
- pyproject.toml / setup.cfg: source of test command, lint rules, and packaging/runtime constraints.
- README.md (configuration section): should be updated if required env vars are user-facing setup requirements.

## Technical Context and Constraints

- Language / framework: Python CLI (argparse/click/typer compatible approach).
- Runtime or platform constraints: Must work cross-platform; use os.environ only, no shell-specific behavior.
- Existing conventions to preserve: Keep current error/reporting style and current exit code semantics where possible.
- Dependencies or interfaces affected: CLI entrypoint imports new validator; config constants may be centralized.
- Validation surface: unit tests for validator logic + CLI integration test for startup failure path.

## Assumptions / Open Questions

- Assumption: Required env var names can be defined as a static list in code (or a single existing config module).
- Assumption: Startup validation should run for all commands, not a command subset.
- Open question: Which exact non-zero exit code is preferred for config errors (commonly 2 for CLI usage errors or 1 for generic failure)?
- Risk if wrong: Inconsistent automation behavior if scripts depend on a specific exit code.

## Recommended Design

Use a small, isolated validator module (for example, src/config_validation.py) with a pure function like validate_required_env(required_vars: list[str], environ: Mapping[str, str] = os.environ) -> list[str]. The function returns missing variable names (sorted), while the CLI entrypoint decides how to format and emit the error and which exit code to use.

This separation keeps logic easy to test, avoids tight coupling to CLI framework internals, and enables future reuse (for preflight checks or diagnostics commands) with minimal refactor.

## Implementation Slices

### Slice 1: Define Validation Contract

- Outcome: Required-env validation logic exists as a pure, testable module API.
- Files: src/config_validation.py, src/config.py (or settings file)
- Dependencies: Confirm canonical list/source of required env vars.

### Slice 2: Wire Startup Enforcement

- Outcome: CLI exits before command execution when validation fails, with clear missing-vars message.
- Files: src/cli.py (or src/main.py), possibly src/errors.py for shared error formatting
- Dependencies: Slice 1 complete.

### Slice 3: Test and Docs Alignment

- Outcome: Automated tests and docs reflect startup validation behavior and expected env variables.
- Files: tests/test_config_validation.py, tests/test_cli_startup.py, README.md
- Dependencies: Slices 1-2 complete.

## File-by-File Implementation Map

- src/config_validation.py: Add validator function, missing-vars detection, and deterministic sorting.
- src/config.py: Add REQUIRED_ENV_VARS constant or expose existing required list for validator consumption.
- src/cli.py (or src/main.py): Invoke validator at startup; if missing exists, print clear error and exit non-zero.
- src/errors.py (optional): Add helper to standardize configuration error rendering.
- tests/test_config_validation.py: Unit-test edge cases (all present, one missing, many missing, empty values policy).
- tests/test_cli_startup.py: Integration-style tests for exit code and error output content.
- README.md: Document required env vars and example startup failure output.

## Validation Plan

- Automated: Run unit and CLI tests (for example, pytest tests/test_config_validation.py tests/test_cli_startup.py).
- Automated: Run existing lint/type checks configured in pyproject.toml or setup.cfg.
- Manual: Execute CLI with full env and with one/many vars removed; verify clear list of missing names and non-zero exit.
- Review focus: Startup control flow ordering, message clarity, deterministic ordering, and backward compatibility of exit behavior.

## Next-Agent Kickoff

1. Read the files listed in Relevant Findings and confirm actual path names in this repository.
2. Implement Slice 1 first with tests, then wire Slice 2, then complete Slice 3.
3. Resolve the open exit-code question before finalizing integration tests.
4. Re-run full validation commands and include sample failure output in handoff-back notes.
