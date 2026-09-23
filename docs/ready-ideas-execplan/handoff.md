# Ready ideas ExecPlan handoff

## Goal and status

Create one implementation-ready ExecPlan for all eight Ready problems in `docs/ideas.md`. The Wayfinder map is [`map.md`](map.md). Provider Hook Capabilities and the first three Ready problem tickets, including [Security Hook Notifications](tickets/security-hook-notifications.md), are closed. Five other problem tickets and ExecPlan Integration remain open. No ExecPlan or implementation exists yet.

## Next step

Read [`map.md`](map.md), then claim [Repository State Guardrails](tickets/repository-state-guardrails.md), the next Ready problem. Resolve its decision with the user, then update its ticket and map. Resolve one Wayfinder ticket per session.

## Decisions and corrections

- Keep all eight underlying problems in scope, including Copilot, Gemini, and Codex on supported platforms. Use one integrated ExecPlan with independently verifiable milestones.
- Windows acceptance requires automated tests and a documented live-check checklist; a live Windows run is not a completion gate.
- User saw the same notice in Copilot and Gemini. Codex logs also show it under explicit `rtk read` output. Cover any platform with a verified misleading notice.
- User rejected dependence on an unpublished RTK release and agreed to test a pinned prerelease before switching agent sessions. [RTK Setup Warning](tickets/rtk-setup-warning.md) selects already-published `dev-0.50.0-rc.451` with command-scoped `RTK_SUPPRESS_HOOK_WARNING=1` and provider pre-tool rewrites. Global config and normal terminal commands stay unchanged.
- RTK notice comes from explicit CLI calls. `hooks/families/rtk.py:187-220` captures and discards RTK hook stderr. Stable v0.49.0 lacks suppression. PR #776 added the flag to prerelease code. No stderr wrapper is needed.
- [Markdown Health Hook](tickets/markdown-health-hook.md) validates entire touched `.md`/`.markdown` files after edits and before completion. It covers deterministic syntax/structure and workspace-local file, image, and heading links only. It skips web and outside-workspace targets, adds no dependency, and requires bounded repair attempts for definite findings. Checker failures warn. Scope includes local Copilot CLI and VS Code, Gemini CLI, and Codex; user excluded Copilot cloud because it cannot load user-level hooks. Gemini `AfterAgent` delivery needs deployed-version proof or a tested fallback.
- User added required low-noise auditing for Markdown Health Hook: one entry per nonempty validation batch for pass, fail, or incomplete, with sorted workspace-relative checked paths, total and omitted counts, finding count, and session/event context. Cap one line at 4 KiB, suppress only unchanged duplicate final checks, log no document contents or link targets, and warn if audit write fails. Preserve Copilot/Gemini and Codex native audit formats.
- [Security Hook Notifications](tickets/security-hook-notifications.md) uses consistent native block/warning messages on local Copilot CLI/VS Code, Gemini, and Codex. Tool Guardian shows the matched operation plus leading input context as one redacted, single-line excerpt capped at 160 characters; unsafe content is omitted. Its existing guard log records the same excerpt, never raw input. scan-secrets names the safe action and generic finding without matched values in the banner. Warnings do not change execution. Codex needs new user-level security hook registration. Copilot cloud is outside this user-level feature.

## Evidence and verification

- Codex command and output: `/Users/adam/.codex/sessions/2026/09/22/rollout-2026-09-22T14-30-22-01a0cb06-e92e-7253-af24-d3440bb7a214.jsonl:16-19`. Output starts with the missing-hook notice. The log proves display, not whether an automatic hook is present.
- Provider research: [`research/provider-hook-capabilities/findings.md`](research/provider-hook-capabilities/findings.md). Installed behavior can differ from repository sources.
- Official `dev-0.50.0-rc.451` macOS arm64 archive matched release SHA-256 `05a32507b07dc38bca835808deb8f32bd182446e8adc90b00209deda0404d321`. Isolated tests confirmed flag hides only missing-hook notice; outdated-hook prompt, missing-file error, stdout, and exit codes remained correct. Stable v0.49.0 ignored flag. Verified prerelease sits beside stable at `/Users/adam/.local/bin/rtk-dev-0.50.0-rc.451`; no agent session switched. Archive binary reports `rtk 0.48.0` despite rc.451 tag, so verify provenance with tag and checksum.
- Isolated `rtk hook gemini` smoke returned valid rewrite JSON. Copilot and Codex sample payloads exited `0` without JSON; exact provider envelopes and compatibility remain unproven. Existing repository RTK hook tests use fake binaries.
- Markdown hook repo survey found no general Markdown linter or remote link checker. `scripts/lint-okf.py:529-570` only scans `.agents/instructions/` and `.agents/memory/`; provider registrations currently lack a user-level Markdown validator. See the ticket for contract links and acceptance cases.
- Audit convention: `hooks/families/audit.py:65-149` writes sanitized, locked, owner-only one-line Copilot/Gemini entries to each provider's `hooks/audit.log`; `.codex/hooks/load-required-skills.py:49-80` writes owner-only key/value lines to `~/.codex/hooks/logs/audit.log`. Markdown auditing must follow both forms.
- Security hook survey: `hooks/families/tool_guard.py:636-674` discards matched action text and formats category/severity only; `:593-633` has a 160-character sanitizer for tool names. `hooks/families/scan_secrets.py:901-905` emits a generic potential-secret message. `.codex/global-hooks.json` has no security hook registration. Generated Copilot/Gemini hooks derive from `hooks/families/`, so implementation must edit canonical source and regenerate outputs.
- Earlier map validation checked ten ticket dependencies and twelve local Markdown links. Markdown ticket closure passed `git diff --check`, eight local-link checks across edited planning files, and `./scripts/lint-okf.py`. Security Hook Notifications planning diff passed `git diff --check`; no RTK or security hook code changed. No live Windows run was performed.
- Branch: `codex/ready-ideas-execplan`.

Use `wayfinder` and `grilling` for the next ticket, then `exec-plans` when writing the destination plan.
