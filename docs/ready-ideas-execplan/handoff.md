# Ready ideas ExecPlan handoff

## Goal and status

The Wayfinder destination is complete: one [ExecPlan](ExecPlan.md) covers all eight former Ready problems with separate acceptance milestones, shared hook setup, and final integration. All tickets in [the map](map.md) are closed. [Ideas](../ideas.md) links to the plan under `Planned`. No feature implementation has begun, and all ten ExecPlan milestones remain open.

## Next step

When implementation begins, open `ExecPlan.md` and start milestone 1, Read Only Orientation. Capture the existing Git status and diffs before editing, then follow the plan's orientation and test steps. Keep `Progress`, milestone status, and the living decision sections synchronized. Use the `exec-plans` and `tdd` skills for source edits; run `update-agent-docs` once at the end of an implementation work session.

## Decisions and constraints

- The user accepted the milestone order and one integrated ExecPlan. Windows-specific hook work requires native automated tests and a precise supplemental live-check procedure; a live Windows run is not a completion gate.
- The user later narrowed Disposable Probe Files: edit only `.gemini/GEMINI.md`, `.copilot/copilot-instructions.md`, and `.codex/AGENTS.md`. Do not add installer checks, local agent runs, automated Windows checks, or a Windows checklist for that milestone. Keep it separate from PowerShell Authoring Guidance, which has broader verification.
- RTK Setup Warning uses already-published, checksum-verified `dev-0.50.0-rc.451` beside stable RTK with command-scoped `RTK_SUPPRESS_HOOK_WARNING=1` for explicit agent commands. It does not depend on a future release or strip stderr. The macOS arm64 SHA-256 is `05a32507b07dc38bca835808deb8f32bd182446e8adc90b00209deda0404d321`; the archive binary reports `rtk 0.48.0`, so its version string cannot prove provenance.
- Shared hook setup must add a baseline Codex scan-secrets adapter before Scan Secrets Shutdown. That scanner milestone then proves bounded, file-backed Git capture in Copilot, Gemini, and Codex. Security Hook Notifications upgrades wording later.
- Copilot cloud remains outside the user-level Markdown and security notification milestones. Provider hooks cannot guarantee interception of arbitrary child-process writes into Git metadata. The plan states these limits and fallback behavior.

## Review findings and evidence

- A read-only ExecPlan audit found four gaps: `docs/ideas.md` disposition lacked a completed step, Codex scanner proof came too late, deployed hook probes lacked executable steps, and final regression reused milestone 9's tag. These were corrected in `ExecPlan.md`. A second review found the probe did not exercise timeout; milestone 4 now includes one-second timeout settings, a three-second delayed handler, outer watchdog, provider result recording, and exact cleanup. The reviewer re-checked this correction and reported PASS.
- `docs/ready-ideas-execplan/ExecPlan.md` holds full source locations, commands, acceptance evidence, recovery, and all eight decisions. Closed tickets under `tickets/` preserve decision detail; `research/provider-hook-capabilities/findings.md` preserves official provider contract links.
- Planning verification on 2026-09-23: `rtk git diff --check` and `rtk test python3 scripts/lint-okf.py` passed. Focused Python checks confirmed all local links across five affected planning files resolve; `docs/ideas.md` no longer has `## Ready`; ExecPlan has ten `Status: open` and ten `Acceptance: not met` markers; each milestone tag appears once; and the plan has no trailing whitespace. No implementation, installed-provider smoke, or native Windows test was run.
- Worktree branch: `codex/ready-ideas-execplan`. Planning edits are `docs/ideas.md`, `docs/ready-ideas-execplan/ExecPlan.md`, this handoff, `map.md`, and `tickets/execplan-integration.md`. No provider instruction or hook source file changed.
