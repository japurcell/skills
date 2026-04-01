# Feature-Dev Response: CLI Config-Validation Module

## Understanding

**Track: Standard** — this is a bounded but non-trivial feature: one new module, one entrypoint integration, and a full TDD + review workflow. The request asks to stop before implementation and produce a concrete handoff artifact, so the work here covers Phases 1–4 of the feature-dev workflow.

Because there is no real codebase to explore, reasonable Python CLI conventions are assumed (src layout, `cli.py` entrypoint, `pytest`). All assumptions are documented in the plan with risk assessments.

---

## Relevant Findings

| Item         | Detail                                                                     |
| ------------ | -------------------------------------------------------------------------- |
| Language     | Python 3.9+, stdlib only (`os`, `sys`) — no new runtime dependencies       |
| Entrypoint   | `src/<package>/cli.py` or `__main__.py` — call `validate_env()` here first |
| New module   | `src/<package>/config.py` — does not yet exist                             |
| New tests    | `tests/test_config.py` — written first per TDD                             |
| Test runner  | `pytest` with `monkeypatch` for env-var control                            |
| Error target | `stderr` + `sys.exit(1)` — CLI convention                                  |

---

## Open Questions

None blocking. All material decisions are resolved:

- **Exit strategy**: `sys.exit(1)` to `stderr` (not raise, not `stdout`) — matches CLI convention.
- **Required var list**: hardcoded constant `REQUIRED_ENV_VARS` in `config.py`; injectable via parameter for testability.
- **Scope**: no value parsing, no `.env` loading.

One soft assumption to verify before implementing: confirm no existing `config.py` at the target path.

---

## Recommendation

Create a single-function module (`config.py`) with a `REQUIRED_ENV_VARS` constant and a `validate_env(required=None)` callable. Call it once at the top of the CLI entrypoint. This is the smallest change that satisfies the requirement, is easy to test, and leaves no global side effects on import.

---

## Implementation Map

1. **Write failing tests** (`tests/test_config.py`) — red state confirmed by `ImportError`
2. **Implement `config.py`** — green
3. **Integrate into entrypoint** — smoke-test passes
4. **code-simplifier refactor pass** — independent subagent reviews `config.py` + tests
5. **code-reviewer pass** — independent subagent reviews full changeset; fix high-severity findings

Validation plan includes: `pytest` with 100 % coverage check, `mypy`/`ruff` lint, and a manual smoke test (`unset DATABASE_URL && python -m <package>` → exit 1 with listed variable name).

---

## Artifact Status

Handoff artifact written to:

```
.agents/scratchpad/cli-config-validation/handoff-plan.md
```

Full path in this workspace:

```
/home/adam/.agents/skills/feature-dev-workspace/iteration-10/eval-2-cli-config-validation-module-handoff/with_skill/run-1/outputs/.agents/scratchpad/cli-config-validation/handoff-plan.md
```

The artifact is **ready for implementation**. A receiving agent can begin with Slice 1 (write failing tests) immediately with no additional discovery required.
