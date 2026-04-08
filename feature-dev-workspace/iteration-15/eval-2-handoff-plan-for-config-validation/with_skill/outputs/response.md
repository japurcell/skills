# Feature-Dev Skill Response: Config Validation Module

## Skill Execution

**Track chosen**: Standard

The request is well-specified in behavior (check env vars, exit with clear error), but touches multiple files (new module + CLI entry point + tests) and carries one meaningful design decision: how the required-vars list is declared. Standard track is appropriate.

---

## Understanding

Add a `config_validator` module to a Python CLI tool that runs at startup, checks for required environment variables, and exits with a message listing all missing ones. No specific codebase was provided, so the plan is written for a canonical Python CLI project (Click-based, `src/` layout, pytest) with explicit instructions for the implementing agent to verify paths before writing code.

---

## Relevant Findings

No live codebase — findings are architecture assumptions:

- `src/<package>/cli.py`: CLI entry point; where `validate_env()` will be called
- `src/<package>/config_validator.py`: new module to create
- `tests/test_config_validator.py`: new test file (TDD first)
- `pyproject.toml` / `setup.cfg`: package name and test runner config

---

## Open Questions

One materially important open question:

> **How should required vars be declared?** Hard-coded list in the validator module (simplest, single source of truth) vs. passed by the caller (needed if multiple CLI entry points exist) vs. read from config file (needed if the team already manages config declaratively). **Default assumption**: hard-coded list in module, with `required` parameter accepted for testability. Implementing agent should check for an existing `config.py`/`settings.py`/`pydantic-settings` pattern before creating a new file.

---

## Recommendation

**Single-function validator with a declarative list and `sys.exit(1)`** — not exceptions. Exceptions require callers to catch them; `sys.exit` + `print(stderr)` is the standard CLI idiom. The function accepts `required` as an argument to make it unit-testable without monkeypatching module globals.

```python
def validate_env(required: list[str] = REQUIRED_ENV_VARS) -> None:
    missing = [var for var in required if not os.environ.get(var)]
    if missing:
        lines = ["Missing required environment variables:"]
        lines += [f"  - {var}" for var in missing]
        print("\n".join(lines), file=sys.stderr)
        sys.exit(1)
```

---

## Implementation Map

| File | Action |
|------|--------|
| `src/<package>/config_validator.py` | Create: `REQUIRED_ENV_VARS` list + `validate_env()` |
| `tests/test_config_validator.py` | Create (TDD first): 4 unit tests |
| `src/<package>/cli.py` | Edit: import + call `validate_env()` at top of entry fn |
| `tests/test_cli_integration.py` | Create: smoke test with subprocess or CliRunner |

**Slices**: (1) Core module with TDD → (2) CLI integration → (3) Integration test

---

## Validation Plan Summary

Three required explicit steps:
1. **TDD red-green-refactor**: write failing tests first, implement to green, refactor
2. **code-simplifier pass**: after green, simplify `config_validator.py` and its tests
3. **Independent code-reviewer**: correctness (all vars listed), security (no values printed), conventions

---

## Artifact Status

Handoff plan created at:

```
.agents/scratchpad/config-validation-module/handoff-plan.md
```

Full path: `/Users/adam/.agents/scratchpad/config-validation-module/handoff-plan.md`

The artifact contains the complete implementation guide — goal/non-goals, findings, technical context, assumptions, recommended design with code sketch, ordered implementation slices, file-by-file map, full validation plan with explicit TDD/simplifier/reviewer steps, and next-agent kickoff instructions. An implementing agent can proceed directly from that file without repeating discovery.
