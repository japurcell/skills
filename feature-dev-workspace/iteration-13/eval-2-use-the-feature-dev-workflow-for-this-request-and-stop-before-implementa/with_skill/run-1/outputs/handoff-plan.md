# Handoff Plan: Configuration Validation Module for Python CLI

## Artifact Metadata
- Status: Ready for implementation
- Track: Standard
- Next Step: Begin Phase 5 implementation using TDD (red-green-refactor)
- Owner: Next implementation agent

## Goal and Non-Goals
Goal
- Add a startup configuration-validation module to a Python CLI tool that checks required environment variables and exits with a clear error listing missing variables.

Non-Goals
- No remote config backends or secrets-manager integration in this slice.
- No runtime hot-reload of environment variables.
- No broad CLI redesign.

## Relevant Findings and Source Files
1. /home/adam/.agents/skills/feature-dev/SKILL.md
- Why it matters: Defines mandatory workflow constraints for implementation and review, including TDD and Phase 6 gates.
2. /home/adam/.agents/skills/feature-dev/references/handoff-plan-template.md
- Why it matters: Provides canonical handoff structure and required sections for reuse.

## Technical Context and Constraints
- Target runtime: Python CLI process with a single startup entry path.
- Behavior requirement: validate required env vars before command execution.
- Failure mode: if any required vars are missing, print explicit error containing complete missing list and exit non-zero.
- Maintainability: required var list should be centralized, not duplicated across commands.

## Open Questions (Blocking Only)
1. Which exact environment variable names are required in production vs local dev?
- Risk if unresolved: false failures or missing protection in real deployments.
2. Should empty-string values count as missing?
- Risk if unresolved: inconsistent validation behavior across environments.
3. Preferred error channel: stderr only, or stderr + structured logging?
- Risk if unresolved: observability mismatch with current CLI diagnostics.

## Assumptions (If Questions Are Unanswered)
- Required vars will be provided as a single authoritative list.
- Empty string is treated as missing.
- Errors are printed to stderr and process exits with code 1.

## Recommended Design and Trade-offs
Recommended
- Introduce a dedicated `config_validation` module with:
1. `find_missing_env_vars(required_vars) -> list[str]`
2. `validate_required_env_vars(required_vars)` that raises a custom error when missing.
- Call validation once at CLI startup before command dispatch.
- Catch the validation error at top-level CLI entry to print a single user-friendly message and exit 1.

Trade-offs
- Centralized startup check is simple and consistent, but it validates variables even for commands that might not use all of them.
- Per-command validation is more precise but adds duplication and behavior drift risk.
- Recommendation favors centralized validation first; command-specific refinement can be a later enhancement.

## Ordered Implementation Slices
1. Red: add tests for success path (all vars present), missing subset, all missing, empty-string handling.
2. Green: implement validation functions and custom error object.
3. Refactor: improve naming and message formatting while keeping tests green.
4. Integrate startup hook in CLI entrypoint and add integration-style test for exit behavior.
5. Final polish for error wording and deterministic ordering of missing variable names.

## File-by-File Implementation Map
1. `src/config_validation.py`
- New module with missing-var detection and validator entrypoint.
2. `src/cli.py`
- Wire startup validation before command execution; catch/print/exit behavior.
3. `tests/test_config_validation.py`
- Unit tests for validation logic and message content.
4. `tests/test_cli_startup_validation.py`
- Integration test for startup failure behavior and exit code.

## Validation Plan
1. TDD completion check
- Demonstrate explicit red-green-refactor loop for validation logic and CLI startup integration.
2. code-simplifier refactor pass
- Launch independent code-simplifier subagent after implementation to identify simplification/refactor opportunities.
3. independent code-reviewer review
- Launch independent code-reviewer subagent(s) to assess correctness, conventions, and risk.
4. Test and quality commands
- Run unit/integration tests and project lint checks required by repo CI.
5. Runtime sanity check
- Execute CLI locally with missing env vars and confirm exact error formatting + non-zero exit.

## Review Checkpoints
- Missing variable list is complete, deterministic, and human-readable.
- Error path is consistent across commands.
- No command runs before validation gate.
- Tests cover both presence and absence scenarios.

## Next-Agent Kickoff Steps
1. Confirm authoritative required-var list with maintainer.
2. Implement tests first (red).
3. Implement minimum logic for green.
4. Perform refactor pass.
5. Run quality review subagents and address high-severity findings.
