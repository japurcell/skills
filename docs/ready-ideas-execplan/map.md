## Destination

Produce one self-contained, implementation-ready ExecPlan at `docs/ready-ideas-execplan/ExecPlan.md` covering all eight problems in the Ready section of `docs/ideas.md`. Its independently verifiable milestones must cover Copilot, Gemini, and Codex on supported platforms. Windows-specific reports require automated tests and a precise live-check checklist; live Windows runs are not an acceptance gate.

## Notes

This map plans the work; it does not implement the eight changes. Keep each underlying problem in scope even when its proposed fix proves unsuitable. Use the `exec-plans` skill for the destination, `grilling` for human decisions, and `research` for external facts. The referenced `domain-modeling` skill is not installed, so use Wayfinder's explicit question, dependency, and resolution structure. `docs/ideas.md` and generated-hook rules in `.agents/instructions/hooks.md` provide starting context. Installed hook behavior differs from repository source and must be distinguished in the ExecPlan.

## Decisions so far

- [Provider Hook Capabilities](tickets/provider-hook-capabilities.md): provider-specific hook contracts permit pre-tool checks, with different display, timeout, trust, and Windows rules.
- [RTK Setup Warning](tickets/rtk-setup-warning.md): use command-scoped `RTK_SUPPRESS_HOOK_WARNING=1` with checksum-verified, pinned `dev-0.50.0-rc.451` in agent sessions; verify provider compatibility before switching, while stable v0.49.0 stays the terminal default.
- [Markdown Health Hook](tickets/markdown-health-hook.md): check touched Markdown after edits and before completion for deterministic syntax and local link defects; use bounded repair attempts and one low-noise audit entry per validation batch.
- [Security Hook Notifications](tickets/security-hook-notifications.md): show consistent block/warning banners on local provider surfaces; Tool Guardian shows and logs a redacted 160-character action excerpt, while scan-secrets banners omit matched values.
- [Repository State Guardrails](tickets/repository-state-guardrails.md): layer provider path protection, pre-tool checks, and instructions; require full local-change review and explicit approval before a Git command discards work.
- [Scan Secrets Shutdown](tickets/scan-secrets-shutdown.md): replace threaded Git pipe reading with bounded temporary-file capture; discard incomplete output, deny in block mode, warn at session end, and test native Windows hang cases.

## Not yet specified

<!-- FOG START -->
The final milestone order and shared test matrix depend on the remaining Ready item decisions.
<!-- FOG END -->

## Out of scope

Implementing the eight changes during this wayfinding effort. The destination is an ExecPlan for that work.

Copilot cloud agent coverage for [Markdown Health Hook](tickets/markdown-health-hook.md): cloud runs load repository hooks, while this feature is user-level; the user chose local Copilot CLI and VS Code coverage.

Copilot cloud agent coverage for [Security Hook Notifications](tickets/security-hook-notifications.md): cloud runs do not load user-level hooks; the user chose local Copilot CLI and VS Code coverage.

A separate privileged Git service or OS policy allowing only Git to write metadata is beyond this effort. [Repository State Guardrails](tickets/repository-state-guardrails.md) selects layered local protection with documented limits.
