# Handoff: Codex required-skills hook

## Goal

Implement the approved ExecPlan for a user-global Codex CLI `SessionStart` hook that loads `~/.agents/skills/caveman/SKILL.md` and announces `Required skill context loaded from {count} file(s).`.

## Status

- Design tree is closed and every recommendation was accepted.
- ExecPlan is complete at `docs/codex-load-required-skills/execplan.md`; purpose is at line 7, progress at line 11, decisions at line 36, plan of work at line 98, and interfaces/ownership at line 219.
- The user explicitly requested plan creation without implementation. No hook, installer, test, or agent-documentation implementation has started.
- The ExecPlan was moved from `.agents/scratchpad/` to the version-controlled feature directory at the user's request; its self-reference was updated.
- This handoff is feature-scoped at `docs/codex-load-required-skills/handoff.md` beside the ExecPlan.
- The ExecPlan is tracked; this relocated handoff is currently the only untracked working-tree file.

## Next focus

Execute Milestone 1 only when the user asks to execute or continue the plan. Follow the later ownership split in `docs/codex-load-required-skills/execplan.md:259` for the full multi-file effort.

## Exact next step

After execution authorization, read `.agents/memory/INDEX.md` and the ExecPlan, activate `exec-plans` and `tdd`, then create the first failing public-process test in `scripts/test-codex-hooks-startup.sh` for successful `SessionStart(startup)` injection and the exact count-bearing announcement. Run it red before adding `.codex/hooks/load-required-skills.py` or `.codex/global-hooks.json`.

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

## Relevant files and sources

- `docs/codex-load-required-skills/execplan.md:1` — complete implementation authority and validation plan.
- `.copilot/hooks/scripts/load-required-skills.py:22` — existing Copilot output/failure/context behavior for comparison only.
- `.gemini/hooks/scripts/skill-context-injector.py:26` — existing Gemini native hard-stop and announcement behavior for comparison only.
- `.copilot/hooks/hooks.json:160` and `.gemini/global-settings.json:179` — current session-start registrations loading Caveman.
- `scripts/install.sh:1`, `scripts/install.ps1:1`, `scripts/test-install.sh:1`, `scripts/test-install.ps1:1` — later installer integration seams.
- `.agents/instructions/hooks.md:1` and `.agents/memory/testing/hooks.md:1` — runtime rules and validation routes.
- Official contract: `https://learn.chatgpt.com/docs/hooks`, fetched 2026-09-09.

## Verification state

- Confirmed the ExecPlan contains every required living-plan section, accepted announcement, ownership split, and a revision note saying implementation remains unstarted.
- Confirmed the old scratchpad ExecPlan path is absent and `docs/codex-load-required-skills/execplan.md` is tracked.
- No implementation tests, syntax checks, live hook run, installer run, PowerShell run, security review, documentation pass, or OKF lint have run because implementation was explicitly deferred.
- `pwsh` availability is not yet verified.

## Errors and blockers

- `rtk` is unavailable (`command not found`) despite repository preference. Report this once in a resumed execution and use direct targeted commands; do not claim `rtk` ran.
- No design blocker remains. Implementation should wait for explicit execution/continue authorization.

## Suggested skills

- `exec-plans` and `tdd` for every implementation slice.
- `delegate-to-subagents` plus `subagent-model-router` because the approved plan spans multiple files/layers and already defines non-overlapping ownership.
- `addy-security-and-hardening` for stdin/path/config/audit boundaries.
- `openai-docs` and `official-sources` if the Codex hook contract needs re-verification.
- `update-agent-docs`, followed by `okf-authoring`, only at the end of the implementation work session.

## Briefing

Do not redesign settled behavior or start with implementation code. On authorization, use the ExecPlan as the single source of truth, begin with Milestone 1's public failing test, preserve unrelated work, and keep the plan's progress/decision/outcome sections synchronized throughout execution.
