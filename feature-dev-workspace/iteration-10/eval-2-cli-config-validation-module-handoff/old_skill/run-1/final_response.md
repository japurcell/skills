# Feature Development: CLI Config Validation Module

## Understanding

**Track**: Standard

The request asks for a handoff plan for adding a configuration-validation module to a Python CLI tool. The module's job is narrow: check for required environment variables at startup and exit with a clear error listing every missing one. Because this features a new module, entry-point integration, a TDD loop, a code-simplifier pass, and an independent code-reviewer pass, it warrants Standard track treatment. The user explicitly asked to stop before implementation, so this turn produces the handoff artifact and halts.

There is no concrete target codebase to explore, so the plan is written against common Python CLI conventions (argparse/click/typer, pytest, pyproject.toml) with clear instructions for the implementing agent to verify assumptions before writing code.

---

## Relevant Findings

No live codebase was examined. The following assumptions drive the design and should be verified by the implementing agent:

| Location                            | Reason it matters                                                         |
| ----------------------------------- | ------------------------------------------------------------------------- |
| `src/<pkg>/cli.py` or `__main__.py` | Entry point; `validate_env` call goes here before any other startup logic |
| `src/<pkg>/config/`                 | Target sub-package; may not exist yet; needs `__init__.py`                |
| `tests/unit/`                       | Test home for the new `test_config_validation.py` file                    |
| `pyproject.toml`                    | Confirms linting config, test paths, and existing dependencies            |

---

## Architecture Decision

**Single function with injected env mapping** — `validate_env(required: list[str], env: Mapping[str, str] | None = None) -> None`

Injecting `env` keeps `os.environ` out of the function body and makes the function testable without monkeypatching. The function collects _all_ missing variables before exiting (not just the first), so the user sees the full picture in one run.

The `REQUIRED_ENV_VARS` list lives in the entry point rather than in `validation.py`, keeping the module generic and reusable across other tools or call sites.

---

## Recommendation

Implement in four ordered slices:

1. **TDD loop** — write all five unit tests first (red), implement `validate_env` (green), refactor for clarity.
2. **Entry-point integration** — wire the call into `main()` before argument parsing.
3. **Code-simplifier refactor pass** — invoke the `code-simplifier` skill on `validation.py` and its test file.
4. **Independent code-reviewer review** — launch a `code-reviewer` agent with three focuses: correctness/edge cases, security (no value leakage in error output), and test coverage gaps.

---

## Artifact Status

Handoff artifact written to:

```
.agents/scratchpad/cli-config-validation/handoff-plan.md
```

(Stored at: `outputs/.agents/scratchpad/cli-config-validation/handoff-plan.md` in this eval run)

The artifact contains the full implementation map, the TDD red-green-refactor loop for Slice 1, the code-simplifier and code-reviewer instructions for Slices 3–4, and the complete validation plan. Another agent can pick up implementation directly from it without repeating discovery.
