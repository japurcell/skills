# Ready ideas ExecPlan handoff

## Goal and status

Create one implementation-ready ExecPlan for all eight Ready problems in `docs/ideas.md`. The Wayfinder map is [`map.md`](map.md). The map, ten tickets, and provider-hook research were committed as `a66574a5`. Provider Hook Capabilities is closed. RTK Setup Warning is open; seven other problem tickets and ExecPlan Integration remain open. No ExecPlan or implementation exists yet.

## Next step

Read [`map.md`](map.md) and [`tickets/rtk-setup-warning.md`](tickets/rtk-setup-warning.md), then claim the RTK ticket. Confirm the corrected decision with the user: the notice comes from explicit agent-issued `rtk` commands; suppress only the misleading missing-hook notice in agent sessions after verifying stable RTK support; preserve other diagnostics. Decide how the setting reaches those commands. Record the confirmed resolution, close the ticket, and link it from the map. Use a follow-on ticket if delivery remains a separate unresolved decision. Resolve one Wayfinder ticket per session.

## Decisions and corrections

- Keep all eight underlying problems in scope, including Copilot, Gemini, and Codex on supported platforms. Use one integrated ExecPlan with independently verifiable milestones.
- Windows acceptance requires automated tests and a documented live-check checklist; a live Windows run is not a completion gate.
- User saw the same notice in Copilot and Gemini. Codex logs also show it under explicit `rtk read` output. Cover any platform with a verified misleading notice.
- User prefers stable upstream RTK support over a local workaround for RTK 0.49. Hide only the missing-hook notice; preserve errors and outdated-hook prompts.
- Earlier choice of agent-scoped hook rewrites needs revalidation. It was made before the user corrected the warning's origin. Do not assume hook execution emits the notice: `hooks/families/rtk.py:187-220` captures and discards RTK stderr. Hook wiring may still deliver a setting, but that design is not settled.
- Upstream development documentation describes `RTK_SUPPRESS_HOOK_WARNING=1`; local RTK 0.49 does not support it. Verify a stable release before making it an ExecPlan dependency. See [`tickets/rtk-setup-warning.md`](tickets/rtk-setup-warning.md) for source link.

## Evidence and verification

- Codex command and output: `/Users/adam/.codex/sessions/2026/09/22/rollout-2026-09-22T14-30-22-01a0cb06-e92e-7253-af24-d3440bb7a214.jsonl:16-19`. Output starts with the missing-hook notice. The log proves display, not whether an automatic hook is present.
- Provider research: [`research/provider-hook-capabilities/findings.md`](research/provider-hook-capabilities/findings.md). Installed behavior can differ from repository sources.
- Initial map validation checked ten ticket dependencies and twelve local Markdown links. No RTK code or tests changed. No live Windows run was performed. Recheck Markdown links and `git diff --check` after planning edits.
- Branch: `codex/ready-ideas-execplan`. The RTK ticket includes the correction prompted by the user. No other known worktree changes at handoff creation.

Use `wayfinder` and `grilling` to finish the ticket, then `exec-plans` when writing the destination plan.
