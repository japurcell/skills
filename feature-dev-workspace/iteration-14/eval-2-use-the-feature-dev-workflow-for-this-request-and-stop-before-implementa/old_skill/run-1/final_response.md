## Understanding

**Track: Light** — This is a well-bounded, self-contained module with a clear acceptance condition (check env vars at startup, exit with a named list of missing vars). The scope is limited to a new module and one integration point. No significant architectural ambiguity exists.

**Workflow stage: Pre-implementation — producing handoff artifact**

---

## Relevant Findings

Since no live codebase is available for exploration, the findings below reflect the canonical structure of a standard Python CLI. The implementing agent must verify actual paths via Phase 2 exploration.

- `src/cli.py` or `src/__main__.py`: CLI entrypoint — where the validation call is inserted before any command dispatch
- `src/config.py` or `src/settings.py` (assumed): existing home for configuration logic; new module should be co-located or follow this pattern
- `tests/test_config.py` (assumed): existing tests for config-adjacent code — new tests go here or in a parallel file following the same conventions
- `README.md` or `docs/`: may define the canonical list of required environment variables — preventing duplication of the definition

---

## Open Questions

1. **Required variable list source**: Is the list of required env var names already defined somewhere in the codebase, or does the new module own that constant? Risk if wrong: duplicates an authoritative definition and creates drift.
2. **Empty string treatment**: Should a var set to `""` be treated as missing? Risk if wrong: startup passes with empty vars that cause silent failures downstream.

These are the only blocking questions. Everything else can proceed on reasonable defaults.

---

## Recommendation

Add a `validate_env(required: list[str]) -> list[str]` function in a new `src/config_validation.py` module. The function returns the list of missing variable names. The CLI entrypoint calls it before argument parsing, checks the return value, and exits with a descriptive stderr message if any names are returned.

This is simpler and more testable than inline validation at the entrypoint, and more reusable than hard-coding `sys.exit()` inside the library function.

---

## Implementation Map

- `src/config_validation.py` (new): `REQUIRED_ENV_VARS` constant + `validate_env()` function
- `src/cli.py`: add 3–5 lines calling `validate_env()` before command dispatch
- `tests/test_config_validation.py` (new): TDD tests for pass, one missing, multiple missing

---

## Artifact Status

Handoff artifact created at: `.agents/scratchpad/config-validation/handoff-plan.md`

The artifact is complete and ready for direct implementation. The implementing agent should read the actual codebase files first to confirm the paths listed in Relevant Findings before executing the implementation slices.
