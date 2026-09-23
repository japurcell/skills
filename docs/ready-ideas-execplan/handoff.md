# Ready ideas ExecPlan handoff

## Goal and status

Create one implementation-ready ExecPlan for all eight Ready problems in `docs/ideas.md`. The Wayfinder map is [`map.md`](map.md). Provider Hook Capabilities and RTK Setup Warning are closed. Seven other problem tickets and ExecPlan Integration remain open. No ExecPlan or implementation exists yet.

## Next step

Read [`map.md`](map.md), then claim [Markdown Health Hook](tickets/markdown-health-hook.md), the next Ready problem. Resolve its decision with the user and update its ticket and map. Resolve one Wayfinder ticket per session.

## Decisions and corrections

- Keep all eight underlying problems in scope, including Copilot, Gemini, and Codex on supported platforms. Use one integrated ExecPlan with independently verifiable milestones.
- Windows acceptance requires automated tests and a documented live-check checklist; a live Windows run is not a completion gate.
- User saw the same notice in Copilot and Gemini. Codex logs also show it under explicit `rtk read` output. Cover any platform with a verified misleading notice.
- User rejected dependence on an unpublished RTK release and agreed to test a pinned prerelease before switching agent sessions. [RTK Setup Warning](tickets/rtk-setup-warning.md) selects already-published `dev-0.50.0-rc.451` with command-scoped `RTK_SUPPRESS_HOOK_WARNING=1` and provider pre-tool rewrites. Global config and normal terminal commands stay unchanged.
- RTK notice comes from explicit CLI calls. `hooks/families/rtk.py:187-220` captures and discards RTK hook stderr. Stable v0.49.0 lacks suppression. PR #776 added the flag to prerelease code. No stderr wrapper is needed.

## Evidence and verification

- Codex command and output: `/Users/adam/.codex/sessions/2026/09/22/rollout-2026-09-22T14-30-22-01a0cb06-e92e-7253-af24-d3440bb7a214.jsonl:16-19`. Output starts with the missing-hook notice. The log proves display, not whether an automatic hook is present.
- Provider research: [`research/provider-hook-capabilities/findings.md`](research/provider-hook-capabilities/findings.md). Installed behavior can differ from repository sources.
- Official `dev-0.50.0-rc.451` macOS arm64 archive matched release SHA-256 `05a32507b07dc38bca835808deb8f32bd182446e8adc90b00209deda0404d321`. Isolated tests confirmed flag hides only missing-hook notice; outdated-hook prompt, missing-file error, stdout, and exit codes remained correct. Stable v0.49.0 ignored flag. Verified prerelease sits beside stable at `/Users/adam/.local/bin/rtk-dev-0.50.0-rc.451`; no agent session switched. Archive binary reports `rtk 0.48.0` despite rc.451 tag, so verify provenance with tag and checksum.
- Isolated `rtk hook gemini` smoke returned valid rewrite JSON. Copilot and Codex sample payloads exited `0` without JSON; exact provider envelopes and compatibility remain unproven. Existing repository RTK hook tests use fake binaries.
- Initial map validation checked ten ticket dependencies and twelve local Markdown links. This ticket closure passed `git diff --check`, eight local-link checks across edited planning files, and `./scripts/lint-okf.py`. No RTK code or tests changed. No live Windows run was performed.
- Branch: `codex/ready-ideas-execplan`.

Use `wayfinder` and `grilling` for the next ticket, then `exec-plans` when writing the destination plan.
