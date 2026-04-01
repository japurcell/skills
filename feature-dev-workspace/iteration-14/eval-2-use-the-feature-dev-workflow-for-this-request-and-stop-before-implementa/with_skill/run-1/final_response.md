# Feature Dev Workflow: Handoff Plan for Config-Validation Module

## Understanding

The request is to prepare a handoff plan for adding a configuration-validation module to a Python CLI tool. The module should check for required environment variables at startup and exit with a clear error message listing missing ones.

**Track chosen**: Standard — the feature touches the CLI startup path (a cross-cutting concern), requires a design decision about module structure and exit behavior, and the handoff explicitly needs to be reusable by another agent.

Stopping before implementation as requested.

---

## Phase 2: Relevant Findings

Since no concrete codebase was provided, exploration focused on the canonical patterns a Python CLI would use for this kind of validation. The artifact documents which files to read and why. Key patterns identified:

- Validation must hook into the CLI entrypoint before argument parsing or command dispatch
- Standard approach: a dedicated `config_validation.py` module with a single `validate_env()` function that returns missing variable names; exit logic lives at the entrypoint boundary, not inside the library function
- Test approach: use `pytest` with `monkeypatch.setenv`/`monkeypatch.delenv` to simulate missing env vars

---

## Phase 3: Open Questions

Three bounded open questions remain (documented in the artifact with risk framing):

1. Are empty string values treated as missing? (affects filtering logic)
2. Is the required variable list static or dynamically configured? (affects function signature)
3. Should the module be callable from non-CLI contexts? (affects whether to use `sys.exit()` directly or raise)

None of these are blockers for starting implementation — the artifact states reasonable assumptions for each.

---

## Phase 4: Recommended Design

Module-based validator with hard exit at the entrypoint boundary:

- `src/config_validation.py`: `validate_env(required: list[str]) -> list[str]` — returns missing variable names, does not exit
- Entrypoint (`src/cli.py`): calls `validate_env`, prints error to stderr, exits if any missing
- No third-party dependencies; `os.environ` is sufficient

This is preferred over inline validation in the entrypoint (untestable in isolation).

---

## Artifact Status

**Handoff artifact created**: `.agents/scratchpad/config-validation/handoff-plan.md`

The artifact was written following the handoff plan template and contains:

- Concretely filled metadata (status, track, recommended next step — no placeholder bracket values)
- Goal / non-goals
- Relevant findings (each with reason)
- Technical context and constraints
- Bounded open questions with risk framing
- Recommended design with rationale and trade-off
- Implementation slices (3 slices in order)
- File-by-file implementation map (exact changes per file)
- Validation plan with TDD completion, code-simplifier refactor pass, and independent code-reviewer review as named discrete steps
- Next-agent kickoff steps

Another agent can continue from this artifact without repeating discovery.
