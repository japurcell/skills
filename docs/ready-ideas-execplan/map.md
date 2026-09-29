## Destination

Revise the existing, self-contained [ExecPlan](ExecPlan.md) for the current local Copilot, Gemini, and Codex hook system. The revision must use verified stable RTK 0.50.0, retire the repository-state hook and user-global Markdown checker, define a repository-local OKF lint hook, set sparse user-visible lifecycle messages and actionable Tool Guardian denials, and specify a performance-focused review of every high-rate hook. Planning must finish before implementation resumes.

## Notes

This map was reopened on 2026-09-28 after the original implementation. All decision tickets are now closed. The user approved the revised [ExecPlan](ExecPlan.md) and [Windows checklist](windows-live-check.md) on 2026-09-28; execution is active under the ExecPlan. Existing completed milestones record past evidence, not acceptance of withdrawn behavior. On 2026-09-29 the user removed the provider RTK explanation, file-first PowerShell and disposable-probe text, plus the root Git-state section; the related tickets below are historical decisions, not current instruction requirements. The stable RTK installer behavior remains. The user narrowed Markdown Health to a repository-local OKF lint hook, and [Actionable Tool Guardian Denials](tickets/actionable-tool-guardian-denials.md) refines [Security Hook Notifications](tickets/security-hook-notifications.md) without weakening redaction. Wayfinding remains planning only. Distinguish checked-in sources, installed user hooks, and historical test results.

## Decisions so far

- [RTK 0.50.0 Release Facts](tickets/rtk-050-release-facts.md): official stable release and checksummed assets support suppression of the missing-hook warning; command exit-code preservation still needs verification.
- [Stable RTK Simplification](tickets/stable-rtk-simplification.md): require stable RTK before installs, manage persistent warning suppression, keep automatic Copilot/Gemini forwarders, and retire verified owned prerelease rewrite assets.
- [Provider Lifecycle Facts](tickets/provider-lifecycle-facts.md): official event and message contracts differ across Copilot, Gemini, and Codex; the observed required-skills message does not prove every event is visible.
- [Repository OKF Hook Capabilities](tickets/repository-okf-hook-capabilities.md): all local provider surfaces have repository-local turn-end hooks, but their event, trust, and response contracts differ; session-end events cannot require repair.
- [Provider Hook Capabilities](tickets/provider-hook-capabilities.md): provider-specific hook contracts permit pre-tool checks, with different display, timeout, trust, and Windows rules.
- [RTK Setup Warning](tickets/rtk-setup-warning.md): historical prerelease solution superseded by [Stable RTK Simplification](tickets/stable-rtk-simplification.md).
- [Markdown Health Hook](tickets/markdown-health-hook.md): historical workspace checker decision; [Markdown Health Retirement](tickets/markdown-health-retirement.md) supersedes it, and [Repository OKF Hook](tickets/repository-okf-hook.md) will decide the narrower replacement.
- [Markdown Health Retirement](tickets/markdown-health-retirement.md): remove maintained user-global checker code and registrations, keep independent OKF lint and audit history, and document possible installed leftovers without automatic cleanup.
- [Repository OKF Hook](tickets/repository-okf-hook.md): use existing repository lint at Copilot and Gemini turn end, add Codex, remove redundant post-tool OKF runs, bound repair, and audit each result.
- [Security Hook Notifications](tickets/security-hook-notifications.md): show consistent block/warning banners on local provider surfaces; Tool Guardian shows and logs a redacted 160-character action excerpt, while scan-secrets banners omit matched values.
- [Actionable Tool Guardian Denials](tickets/actionable-tool-guardian-denials.md): name exact safe rule causes and limit counts, bound multiple findings, keep redaction and matching logs, and avoid misleading allowlist advice.
- [Repository State Guardrails](tickets/repository-state-guardrails.md): historical hook decision; [Repository State Retirement](tickets/repository-state-retirement.md) supersedes it.
- [Repository State Retirement](tickets/repository-state-retirement.md): remove maintained guard code and registrations, leave old installed copies for manual cleanup, and verify fresh installs. Its original instruction-retention decision was later superseded.
- [Lifecycle Notifications](tickets/lifecycle-notifications.md): independent operational hooks show sparse startup and turn-end results on three CLIs; tool passes stay quiet and live checks prove visibility.
- [High-Rate Hook Performance Review](tickets/high-rate-hook-performance-review.md): audit every retained high-rate registration with direct macOS script timing, evidence-based budgets, and fixes for clear hot-path defects; no live CLI timing gate.
- [Scan Secrets Shutdown](tickets/scan-secrets-shutdown.md): replace threaded Git pipe reading with bounded temporary-file capture; discard incomplete output, deny in block mode, warn at session end, and test native Windows hang cases.
- [Read Only Orientation](tickets/read-only-orientation.md): exempt read-only audits, diff reviews, and reports from mandatory memory pre-reading; load task-relevant guidance and complete full orientation before any edit.
- [PowerShell Authoring Guidance](tickets/powershell-authoring-guidance.md): historical instruction decision; the provider text was later removed.
- [Disposable Probe Files](tickets/disposable-probe-files.md): historical three-file instruction decision; the provider text was later removed.
- [ExecPlan Integration](tickets/execplan-integration.md): order eight independently verifiable outcomes with shared hook setup and final regression in one [ExecPlan](ExecPlan.md); replace the Ready list with its link.
- [Revised ExecPlan Integration](tickets/revised-execplan-integration.md): preserve compact historical evidence, add new milestones in dependency order with separate live gates, and require explicit approval of revised planning docs before source work.

## Not yet specified

<!-- FOG START -->
<!-- FOG END -->

## Out of scope

Implementing hook, generator, installer, or configuration changes during this wayfinding effort. The destination is a revised ExecPlan for that work.

Copilot cloud agent coverage for [Security Hook Notifications](tickets/security-hook-notifications.md): cloud runs do not load user-level hooks; the user chose local Copilot CLI and VS Code coverage.

VS Code Local and Copilot Agent Host coverage for [Repository OKF Hook](tickets/repository-okf-hook.md): the user chose Copilot CLI, Gemini CLI, and Codex CLI only for this repo-local lint behavior. Copilot cloud is not an acceptance surface for that ticket.

Designing a replacement repository-state enforcement service is beyond the user's retirement request. The core Git safety instructions retained by [Repository State Retirement](tickets/repository-state-retirement.md) were later removed from root `AGENTS.md`.
