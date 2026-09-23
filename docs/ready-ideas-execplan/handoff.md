# Ready ideas ExecPlan handoff

## Goal and status

Create one implementation-ready ExecPlan for all eight Ready problems in `docs/ideas.md`. The Wayfinder map is [`map.md`](map.md). Provider Hook Capabilities and RTK Setup Warning are closed. Seven other problem tickets and ExecPlan Integration remain open. No ExecPlan or implementation exists yet.

## Next step

Read [`map.md`](map.md), then claim [Markdown Health Hook](tickets/markdown-health-hook.md), the next Ready problem. Resolve its decision with the user and update its ticket and map. Resolve one Wayfinder ticket per session.

## Decisions and corrections

- Keep all eight underlying problems in scope, including Copilot, Gemini, and Codex on supported platforms. Use one integrated ExecPlan with independently verifiable milestones.
- Windows acceptance requires automated tests and a documented live-check checklist; a live Windows run is not a completion gate.
- User saw the same notice in Copilot and Gemini. Codex logs also show it under explicit `rtk read` output. Cover any platform with a verified misleading notice.
- User prefers stable upstream RTK support over a local workaround for RTK 0.49. Hide only the missing-hook notice; preserve errors and outdated-hook prompts.
- RTK notice comes from explicit CLI calls. `hooks/families/rtk.py:187-220` captures and discards RTK hook stderr. [RTK Setup Warning](tickets/rtk-setup-warning.md) selects agent-scoped command rewrites, with per-command instruction fallback, and leaves global config unchanged.
- Upstream development documentation describes `RTK_SUPPRESS_HOOK_WARNING=1`; latest stable v0.49.0 documentation omits it. Verify a stable release before using this setting. See [RTK Setup Warning](tickets/rtk-setup-warning.md) for source links and acceptance criteria.

## Evidence and verification

- Codex command and output: `/Users/adam/.codex/sessions/2026/09/22/rollout-2026-09-22T14-30-22-01a0cb06-e92e-7253-af24-d3440bb7a214.jsonl:16-19`. Output starts with the missing-hook notice. The log proves display, not whether an automatic hook is present.
- Provider research: [`research/provider-hook-capabilities/findings.md`](research/provider-hook-capabilities/findings.md). Installed behavior can differ from repository sources.
- Initial map validation checked ten ticket dependencies and twelve local Markdown links. This ticket closure passed `git diff --check`, eight local-link checks across edited planning files, and `./scripts/lint-okf.py`. No RTK code or tests changed. No live Windows run was performed.
- Branch: `codex/ready-ideas-execplan`.

Use `wayfinder` and `grilling` for the next ticket, then `exec-plans` when writing the destination plan.
