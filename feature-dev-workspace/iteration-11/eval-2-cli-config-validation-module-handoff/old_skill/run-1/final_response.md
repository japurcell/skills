# Feature-Dev Run: CLI Config Validation Module Handoff

## Understanding

**Request**: Prepare a handoff plan for adding a configuration-validation module to a Python CLI tool that checks for required environment variables at startup and exits with a clear error message listing which are missing.

**Track chosen**: Standard — the feature touches the CLI entry-point, introduces a new module, and has one meaningful design decision (where/when to invoke validation). It is not large enough for Deep, but it is too interconnected for Light.

**Stopping point**: Per the task prompt, execution stops before implementation.

---

## Relevant Findings

No live codebase was provided. The handoff plan is written against conventional Python CLI project structure (src-layout, Click or argparse, `pyproject.toml`). All file paths in the plan are placeholders that the implementing agent must verify.

Key structural observations for a generic Python CLI tool:

- **Entry-point**: `src/<package>/cli.py` or `__main__.py` registered via `[project.scripts]` in `pyproject.toml`.
- **Config constants**: Often a `config.py` or `settings.py` alongside the entry-point; the `REQUIRED_ENV_VARS` list should live there if such a file exists.
- **Test suite**: `tests/` directory using `pytest`; `monkeypatch` is the idiomatic way to test env-var state.
- **No new runtime dependencies**: `os.environ` and `sys.exit` are stdlib; zero additions to `pyproject.toml` required.

---

## Open Questions

1. **`--help` gating**: Should validation fire before `--help` output is shown? Defaulted to _yes_ (simplest implementation); implementing agent should override if the project requires credentials-free help text.
2. **Exit-code registry**: Assumed `sys.exit(1)` is correct. If the project has a dedicated exit-code enumeration, use the appropriate constant.
3. **Logging vs. stderr**: Defaulted to `sys.stderr` for the error message. If the project uses a structured logger at startup, the implementing agent should route through it.

---

## Recommendation

Implement a single `config_validator.py` module with a `validate_env(required, env=None)` function that collects all missing variables and exits once with a formatted list. Wire it as the first call in `main()`. This is simpler than a raise/catch pattern and keeps the module independently testable.

---

## Implementation Map (summary)

| File                                  | Change                                                               |
| ------------------------------------- | -------------------------------------------------------------------- |
| `src/<package>/config_validator.py`   | New — `validate_env()` function                                      |
| `src/<package>/config.py` (if exists) | Add `REQUIRED_ENV_VARS` list                                         |
| `src/<package>/cli.py`                | Import and call `validate_env(REQUIRED_ENV_VARS)` at top of `main()` |
| `tests/test_config_validator.py`      | New — four pytest cases                                              |

---

## Artifact Status

Handoff artifact written to:

```
/home/adam/.agents/skills/feature-dev-workspace/iteration-11/eval-2-cli-config-validation-module-handoff/old_skill/run-1/outputs/.agents/scratchpad/cli-config-validation/handoff-plan.md
```

Status: **ready for implementation**
