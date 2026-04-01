# Feature Dev Response: CLI Config Validation Module

## Understanding

Request: Add a configuration-validation module to a Python CLI tool that checks for required environment variables at startup and exits with a clear error message listing any that are missing.

**Chosen track: Standard** — the work is bounded but touches multiple files (new module, existing entry point, new tests), involves a design decision (where validation lives and how it is structured), and the target codebase was not provided, requiring explicit documented assumptions for a follow-on implementer.

Stopping before implementation as instructed. A file-backed handoff artifact has been written.

---

## Relevant Findings

No target repository was provided. Findings are based on conventional Python CLI project layout:

- `src/<pkg>/cli.py` or `main.py`: Entry point where `validate_config()` must be called first — before argument parsing or any I/O.
- `src/<pkg>/config.py` or `settings.py`: May already exist as the home for env-var reads; consolidate there if it already handles configuration, otherwise keep the validator separate.
- `tests/`: Add `test_config_validator.py` alongside existing test files.
- `pyproject.toml` / `requirements.txt`: Check for existing config-management libraries (pydantic-settings, dynaconf) before adding a custom module.

---

## Open Questions

None blocking. All resolved via stated assumptions:

1. No existing config-management library is in use (if one is, extend it instead).
2. Required var list is static and known at import time.
3. Exit code 1 is acceptable for missing-config errors.
4. Single entry-point (`main()` / `cli()`) — validate there; if multiple subcommand entry points exist, move validation to a shared initializer.

---

## Recommendation

Create a standalone `config_validator.py` module with:

- `REQUIRED_ENV_VARS: list[str]` — static list of required variable names.
- `validate_config(required=None) -> None` — collects **all** missing vars (not just the first), then calls `sys.exit(1)` with a formatted message listing each one. The optional `required` parameter allows tests to inject a custom list without patching the module constant.

Call `validate_config()` as the first statement in `main()` / `cli()`.

**Why this design**: stdlib-only (no new dependencies), fully unit-testable via `monkeypatch`, and keeps validation concerns out of the entry point. The parameterised-`required` approach was chosen over a patching-only approach to make tests self-describing.

**Empty-string handling note**: The implementation uses `os.environ.get(var)` (falsy check), meaning empty-string values are treated as missing. If the project intends empty string as a valid value, switch to `var not in os.environ`. This is the highest-risk assumption and should be confirmed before implementation.

---

## Implementation Map

| File                             | Change                                                                            |
| -------------------------------- | --------------------------------------------------------------------------------- |
| `src/<pkg>/config_validator.py`  | **Create** — `REQUIRED_ENV_VARS`, `validate_config()`                             |
| `src/<pkg>/cli.py`               | **Edit** — add import + `validate_config()` call at top of `main()`               |
| `tests/test_config_validator.py` | **Create** — 4 test cases: all present, one missing, multiple missing, empty list |

---

## Artifact Status

Handoff artifact written to:

```
outputs/.agents/scratchpad/cli-config-validation/handoff-plan.md
```

Full path:
`/home/adam/.agents/skills/feature-dev-workspace/iteration-11/eval-2-cli-config-validation-module-handoff/with_skill/run-1/outputs/.agents/scratchpad/cli-config-validation/handoff-plan.md`

The artifact contains the complete template: goal/non-goals, relevant findings, technical context and constraints, assumptions, recommended design with rationale, three ordered implementation slices, file-by-file implementation map with code, validation plan, and next-agent kickoff steps. A follow-on agent can implement without repeating discovery.
