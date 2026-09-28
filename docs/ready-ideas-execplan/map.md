## Destination

Revise the existing, self-contained [ExecPlan](ExecPlan.md) for the current local Copilot, Gemini, and Codex hook system. The revision must use verified stable RTK 0.50.0, retire the repository-state and Markdown-health hooks, define sparse user-visible lifecycle messages, and specify a performance-focused review of every high-rate hook. Planning must finish before implementation resumes.

## Notes

This map is reopened on 2026-09-28 after the original implementation. Existing closed tickets and milestones record past decisions and evidence, not instructions to preserve behavior the user has withdrawn. This session charts tickets only; no hook or installer implementation starts before the revised plan is approved. Use `exec-plans` for the destination, `grilling` for human decisions, and `research` for external facts. The referenced `domain-modeling` skill is not installed, so use Wayfinder's explicit question, dependency, and resolution structure. Distinguish checked-in sources, installed user hooks, and historical test results.

## Decisions so far

- [RTK 0.50.0 Release Facts](tickets/rtk-050-release-facts.md): official stable release and checksummed assets support suppression of the missing-hook warning; command exit-code preservation still needs verification.
- [Provider Lifecycle Facts](tickets/provider-lifecycle-facts.md): official event and message contracts differ across Copilot, Gemini, and Codex; the observed required-skills message does not prove every event is visible.
- [Provider Hook Capabilities](tickets/provider-hook-capabilities.md): provider-specific hook contracts permit pre-tool checks, with different display, timeout, trust, and Windows rules.
- [RTK Setup Warning](tickets/rtk-setup-warning.md): historical prerelease solution; [Stable RTK Simplification](tickets/stable-rtk-simplification.md) reopens it after the verified 0.50.0 release.
- [Markdown Health Hook](tickets/markdown-health-hook.md): historical checker decision; [Markdown Health Retirement](tickets/markdown-health-retirement.md) supersedes it.
- [Security Hook Notifications](tickets/security-hook-notifications.md): show consistent block/warning banners on local provider surfaces; Tool Guardian shows and logs a redacted 160-character action excerpt, while scan-secrets banners omit matched values.
- [Repository State Guardrails](tickets/repository-state-guardrails.md): historical hook decision; [Repository State Retirement](tickets/repository-state-retirement.md) supersedes it.
- [Scan Secrets Shutdown](tickets/scan-secrets-shutdown.md): replace threaded Git pipe reading with bounded temporary-file capture; discard incomplete output, deny in block mode, warn at session end, and test native Windows hang cases.
- [Read Only Orientation](tickets/read-only-orientation.md): exempt read-only audits, diff reviews, and reports from mandatory memory pre-reading; load task-relevant guidance and complete full orientation before any edit.
- [PowerShell Authoring Guidance](tickets/powershell-authoring-guidance.md): instruct local Gemini, Copilot, and Codex to write multiline PowerShell and reusable automation scripts with native file tools before running saved files; verify installed guidance and agent behavior.
- [Disposable Probe Files](tickets/disposable-probe-files.md): add placement and cleanup rules only to the three provider instruction files; keep permanent tests tracked and avoid a broad probe ignore rule, with no installer or agent-run checks for this milestone.
- [ExecPlan Integration](tickets/execplan-integration.md): order eight independently verifiable outcomes with shared hook setup and final regression in one [ExecPlan](ExecPlan.md); replace the Ready list with its link.

## Not yet specified

<!-- FOG START -->
<!-- FOG END -->

## Out of scope

Implementing hook, generator, installer, or configuration changes during this wayfinding effort. The destination is a revised ExecPlan for that work.

Copilot cloud agent coverage for [Security Hook Notifications](tickets/security-hook-notifications.md): cloud runs do not load user-level hooks; the user chose local Copilot CLI and VS Code coverage.

Designing a replacement repository-state enforcement service is beyond the user's retirement request. Existing agent Git safety instructions remain in force until the retirement ticket decides their future wording.
