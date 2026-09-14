# Handoff: Codex required-skills hook

## Goal

Implement the approved ExecPlan for a user-global Codex CLI `SessionStart` hook that loads `~/.agents/skills/caveman/SKILL.md` and announces `Required skill context loaded from {count} file(s).`.

## Status

- Design tree is closed and every recommendation was accepted.
- The approved feature is implemented across the hook, inactive global template, shared merger, Bash/PowerShell installers, public tests, README, and canonical agent docs. All focused security-review findings have corresponding fixes and available-platform regressions.
- The ExecPlan at `docs/codex-load-required-skills/execplan.md` is synchronized through Milestone 5. Milestones 1-2 meet acceptance; Milestones 3-5 are done with recorded verification gaps.
- The ExecPlan was moved from `.agents/scratchpad/` to the version-controlled feature directory at the user's request; its self-reference was updated.
- This handoff is feature-scoped at `docs/codex-load-required-skills/handoff.md` beside the ExecPlan.
- No commit was created, per user instruction.

## Next focus

User review and commit. If a PowerShell 7 host is available first, run the one outstanding runtime suite.

## Exact next step

Run `pwsh -NoProfile -File scripts/test-install.ps1` on a PowerShell 7 host if available; otherwise inspect the final diff and commit the current work without rerunning a real-home installer.

## Decisions and constraints

- User-global only: install the script under `~/.codex/hooks/` and merge configuration into `~/.codex/hooks.json`; do not add active project-local `.codex/hooks.json`.
- Maintained source layout: `.codex/hooks/load-required-skills.py` plus inactive `.codex/global-hooks.json`.
- Register synchronous `SessionStart` for `startup|resume|clear|compact`, timeout 5 seconds, `additionalContextLimit` 8000; no `SubagentStart`.
- Define `required_skill_files = ["caveman/SKILL.md"]` and `max_context_bytes = 20_000` near the hook's top. No environment override.
- Resolve only below `~/.agents/skills`; reject absolute paths, traversal, and symlink escapes. Strip YAML frontmatter and cap the final UTF-8 context, including markers/prefix.
- Success uses Codex `hookSpecificOutput.additionalContext` and exact `systemMessage` announcement. Required-skill failures exit 0 with parseable `continue: false`, `stopReason`, and `systemMessage: "Required skill context was NOT loaded."`.
- Audit to owner-only `~/.codex/hooks/logs/audit.log`; never log skill contents. Audit failure warns but does not block. Do not port `send-event.py`, SQLite, NDJSON shadow logging, or lifecycle-wide observability.
- Installation must preserve unrelated hooks, recognize the owned handler by its stable installed command path, avoid rewrites when unchanged, atomically replace valid changes, and keep one owner-only `hooks.json.bak`. Invalid/non-object JSON remains untouched.
- Support Bash and PowerShell installers through one standard-library Python merge helper. No new dependencies.
- Non-managed Codex hooks require user review through `/hooks`; do not recommend bypassing trust.

## Review findings and corrections

- User correction: visible output parity was initially omitted from the closed design tree. The exact announcement is now a first-class acceptance requirement in the ExecPlan at lines 7 and 56.
- Ordinary Codex command handlers have no documented `name` identity; installer ownership must use the stable installed command path.
- Matching Codex hooks run concurrently, so no behavior may depend on registration order.
- Keep the Codex implementation runtime-local; repository conventions prohibit cross-directory imports from Copilot or Gemini hook trees.
- Root review follow-up: add public red tests before fixing the hook's final-read input-cap bypass and symlink-following audit directory; replace macOS-only `stat -f` mode assertions with Python standard-library checks.
- Premium review found seven actionable issues. Fixed: lone-surrogate crashes, linked hook/config destinations, broad handler ownership, malformed open-pipe input, unbounded skill reads, audit-file symlinks, and recursive PowerShell chmod of unrelated Codex hooks.
- Focused Premium re-review found three remaining edges. Fixed: ambiguous malformed JSON now stops after a bounded 0.5-second completion window, raw skill files have a separate one-megabyte bound so removable frontmatter does not consume the 20,000-byte context budget, and Windows audit directories/files reject junctions and other reparse points as well as symlinks.
- Three test-edit mistakes placed or indented shell content inside Python heredocs. All were caught by `bash -n` or the public suite before product changes and repaired; future edits to mixed shell/Python test files should run `bash -n` immediately after each patch.
- The initial Premium reviewer dispatch accidentally inherited the parent model. It was interrupted before use and redispatched as recorded with `gpt-5.6-sol`.
- `scripts/test_helpers.py` initially failed only because sandbox policy denied its prescribed `.agents/scratchpad/test-artifacts` directory; the approved rerun passed 14/14.

## Relevant files and sources

- `docs/codex-load-required-skills/execplan.md:1` — complete implementation authority and validation plan.
- `.copilot/hooks/scripts/load-required-skills.py:22` — existing Copilot output/failure/context behavior for comparison only.
- `.gemini/hooks/scripts/skill-context-injector.py:26` — existing Gemini native hard-stop and announcement behavior for comparison only.
- `.copilot/hooks/hooks.json:160` and `.gemini/global-settings.json:179` — current session-start registrations loading Caveman.
- `scripts/install.sh:1`, `scripts/install.ps1:1`, `scripts/test-install.sh:1`, `scripts/test-install.ps1:1` — later installer integration seams.
- `.agents/instructions/hooks.md:1` and `.agents/memory/testing/hooks.md:1` — runtime rules and validation routes.
- Official contract: `https://learn.chatgpt.com/docs/hooks`, fetched 2026-09-10.

## Verification state

- Passed `bash scripts/test-codex-hooks-startup.sh` and `bash scripts/test-install.sh` after all hardening changes.
- Passed Bash syntax, non-writing Python AST syntax, maintained hook JSON parsing, executable source-mode assertions, and `git diff --check`.
- Passed `python scripts/test_helpers.py` (14 tests) after allowing its existing scratchpad fixture writes.
- Premium security review and both focused verification passes completed. The final reviewer confirmed bounded zero-byte/partial-UTF-8 stdin behavior and missing-safe audit-link detection, with no remaining finding in scope.
- OKF: all six touched canonical files have zero diagnostics. Full `./scripts/lint-okf.py` exits 1 with 84 pre-existing diagnostics outside this feature.
- Not run: `scripts/test-install.ps1` or PowerShell parser (`pwsh` absent), real-home installation, live Codex `/hooks` trust/load smoke test.

## Errors and blockers

- `rtk` 0.48.0 is now installed and eligible proxy commands work. Its tracking database cannot initialize in this sandbox (`Operation not permitted`), and it warns that its shell hook is not initialized; use it where eligible but do not claim tracking evidence.
- `pwsh` is not installed (`command not found`), so `scripts/install.ps1` parsing and `scripts/test-install.ps1` remain unverified on this host; do not install dependencies.
- Full OKF lint remains red on 84 out-of-scope legacy migration diagnostics; touched canonical docs are clean.
- No implementation blocker remains. Native Windows execution is the only platform-specific validation gap. Do not commit in this task; the user will commit.

## Suggested skills

- `exec-plans` and `tdd` for every implementation slice.
- `delegate-to-subagents` plus `subagent-model-router` because the approved plan spans multiple files/layers and already defines non-overlapping ownership.
- `addy-security-and-hardening` for stdin/path/config/audit boundaries.
- `openai-docs` and `official-sources` if the Codex hook contract needs re-verification.
- `update-agent-docs`, followed by `okf-authoring`, only at the end of the implementation work session.

## Briefing

Implementation is ready for user review without a commit. Trust the Bash/Python fixture and independent security-review evidence, keep the native Windows and global-OKF gaps explicit, and do not run the real installer unless the user asks because it mutates `~/.codex/hooks.json` and triggers a new `/hooks` trust review.
