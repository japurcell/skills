# Handoff Plan: Configuration Validation Module for Python CLI

**Status**: ready for implementation
**Track**: Standard
**Origin**: feature-dev
**Feature Area**: CLI startup and configuration bootstrap
**Recommended Next Step**: implement directly

## Summary

Prepare a startup-time configuration-validation module for a Python CLI that checks required environment variables before command execution. This handoff uses the Standard track because the behavior is clear but integration points (entrypoint wiring, error formatting, and test seams) span multiple files. Outcome: a clear implementation path that exits early with a deterministic, user-friendly missing-variable report.

## Goal / Non-Goals

- Goal: Validate required environment variables at CLI startup before normal command logic runs.
- Goal: Exit with a clear error message listing all missing environment variables.
- Goal: Keep validation logic centralized and testable independent of CLI parsing.
- Non-goal: Implement advanced schema/type validation (only required-presence checks).
- Non-goal: Introduce new config-file formats or secrets-management integrations.

## Relevant Findings

- src/<cli_package>/__main__.py: primary CLI process entrypoint; best place to fail fast before command execution.
- src/<cli_package>/cli.py: command dispatch layer where startup checks are often currently invoked.
- src/<cli_package>/config.py: existing config constants/defaults should remain source of truth for required env var names if present.
- tests/test_cli_startup.py: integration-level behavior verification for non-zero exit and message text.
- tests/test_config_validation.py: unit-level contract for missing-variable detection and message ordering.
- pyproject.toml: test tooling and entrypoint declarations to align validation invocation path.

## Technical Context and Constraints

- Language / framework: Python CLI (argparse/click/typer style; exact framework to confirm in repo).
- Runtime or platform constraints: must work in non-interactive shells and CI; no prompts.
- Existing conventions to preserve: existing error formatting, logger usage, and current exit-code semantics.
- Dependencies or interfaces affected: startup entrypoint, config constants, and CLI error handling path.
- Validation surface: unit tests for validator function plus CLI startup tests for process exit and stderr/stdout message.

## Assumptions / Open Questions

- Assumption: the project has a single canonical CLI startup path where a guard can run once.
- Assumption: required env vars can be represented as a static list/tuple in code.
- Open question: preferred exit code for missing configuration (commonly 2 for usage/config error, or existing project standard).
- Risk if wrong: inconsistent automation behavior or mismatch with current scripting expectations.

## Recommended Design

Use a dedicated validator module (`config_validation.py`) exposing a pure function that accepts an env mapping and required keys, returning missing keys in deterministic order. Add a small startup guard in the CLI entrypoint that calls this validator before command execution; if missing keys exist, print a concise, multi-line error and exit immediately with the agreed non-zero code. This is preferred over scattering checks through command handlers because it guarantees uniform behavior, avoids duplicate logic, and simplifies testing.

## Implementation Slices

### Slice 1: Add validator module

- Outcome: reusable required-env validation utility exists with deterministic output.
- Files: src/<cli_package>/config_validation.py, tests/test_config_validation.py.
- Dependencies: confirm canonical list of required env vars and ordering convention.

### Slice 2: Wire startup guard into CLI entrypoint

- Outcome: CLI exits before command execution when required env vars are missing.
- Files: src/<cli_package>/__main__.py (or src/<cli_package>/cli.py), tests/test_cli_startup.py.
- Dependencies: Slice 1 complete; agreed exit code and message style.

### Slice 3: Refine user-facing error output

- Outcome: clear error text lists exactly which env vars are missing and how to fix.
- Files: src/<cli_package>/errors.py (if present) or entrypoint formatter section, tests/test_cli_startup.py.
- Dependencies: Slice 2 complete; preserve project conventions for stderr/logging.

## File-by-File Implementation Map

- src/<cli_package>/config_validation.py: add `find_missing_required_env(required_keys, env=os.environ)` that returns ordered missing keys and helper formatter.
- src/<cli_package>/config.py: define/confirm `REQUIRED_ENV_VARS` tuple to centralize required key names.
- src/<cli_package>/__main__.py: invoke validator before command execution; emit clear message and `raise SystemExit(<code>)` on failure.
- src/<cli_package>/cli.py: if this is true command entrypoint, place guard here instead of `__main__.py`.
- tests/test_config_validation.py: cover no-missing and missing-subset cases with deterministic ordering.
- tests/test_cli_startup.py: verify non-zero exit and exact missing-vars message content.

## Validation Plan

- TDD red-green-refactor completion: write failing unit and startup tests first, implement minimal pass, then refactor while keeping green.
- Automated: run targeted tests for validator and CLI startup (for example `pytest tests/test_config_validation.py tests/test_cli_startup.py`).
- Manual: run CLI with all vars set and with one/two vars removed; verify early exit and readable message.
- Code-simplifier refactor pass: run an independent simplification pass focusing on validator API clarity and duplicated error formatting.
- Independent code-reviewer review: run an independent review focused on startup control-flow correctness, exit semantics, and test coverage gaps.
- Review focus: ordering stability of missing keys, stderr/stdout destination, and backward compatibility of exit code.

## Next-Agent Kickoff

1. Resolve package path placeholders (`<cli_package>`) and identify the true startup file.
2. Read the files listed in Relevant Findings and confirm framework-specific entrypoint flow.
3. Execute slices in order, preserving TDD red-green-refactor discipline.
4. If exit code convention is unclear, pause and ask before finalizing user-facing behavior.
5. Re-run validation plan and hand back with test evidence and any residual risks.
