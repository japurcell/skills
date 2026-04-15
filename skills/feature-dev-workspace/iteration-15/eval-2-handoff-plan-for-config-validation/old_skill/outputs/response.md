# Feature-Dev Skill Response — Configuration Validation Module

## Understanding

**Process track chosen**: Standard

This request asks for a handoff plan (explicitly stopping before implementation) for a new `config_validation` module in a Python CLI tool. The feature is well-described but has one real design decision (where to declare the required-vars list) and touches multiple files (new module, entry point, tests, docs). Standard track is appropriate.

No existing codebase was provided, so exploration is based on standard Python CLI conventions. The implementing agent's first step is to read the actual entry point and test files before coding.

## Relevant Findings

No repository was supplied. Key files the implementing agent must read before proceeding:

- Entry point (`cli.py` / `src/<package>/__main__.py` / `main.py`): startup order and import style
- `tests/`: confirms test runner (pytest assumed) and fixture patterns
- `pyproject.toml` / `setup.cfg`: package layout, confirms where to place the new module
- `README.md`: existing documentation conventions

## Open Questions

1. **Constant placement**: Should `REQUIRED_VARS` live at the call site (entry point) or in a centralized `constants.py`? Recommend call-site for visibility; adjust if the team prefers centralized config.
2. **Exit code**: Is `1` the project's standard non-zero exit, or is there a convention for distinct codes?

Assumptions made (proceed unless wrong):
- `pytest` is the test runner
- Errors go to `stderr`, exit code `1`
- Required variable names are known at code-write time

## Recommendation

**Thin validation function called from entry point with an explicit list.**

`validate_env_vars(required: list[str], env: dict | None = None) -> None` — pure function, injectable `env` parameter for testability, prints formatted error to `stderr` and calls `sys.exit(1)` if any vars are absent.

## Implementation Map (summary)

| File | Action |
|---|---|
| `src/<package>/config_validation.py` | Create — validation function |
| `tests/test_config_validation.py` | Create — TDD-first tests |
| `cli.py` / `__main__.py` | Edit — hook call at startup |
| `README.md` | Edit — document required vars |

## Artifact Status

Handoff artifact created at:

```
/Users/adam/.agents/skills/.agents/scratchpad/config-validation/handoff-plan.md
```

The artifact contains: goal/non-goals, relevant files to read, technical context, assumptions/open questions, recommended design with rationale, ordered implementation slices, file-by-file implementation map, and a validation plan with explicit TDD red-green-refactor, code-simplifier, and code-reviewer steps named as discrete checkpoints.
