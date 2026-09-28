# Ready ideas planning restart handoff

## Goal and status

The user changed requirements on 2026-09-28 and invoked Wayfinder. The [map](map.md) is reopened with new tickets. The [ExecPlan](ExecPlan.md) and [Windows checklist](windows-live-check.md) are marked historical and paused as execution guides. No hook source, registration, installer, or installed user file has changed in this restart.

The prior implementation remains on `codex/ready-ideas-execplan` through `c0d9ca34`. Its six fixed-point review findings were repaired and cleared by their original reviewers. Existing repository-state and Markdown-health hooks, prerelease RTK rewrite path, and user-level installations still represent the old design. Do not claim new requirements are implemented merely because the old checks passed.

## New requirements

- Official research verified stable RTK 0.50.0 and its `RTK_SUPPRESS_HOOK_WARNING` support. Plan replacement of the pinned prerelease route and removal of unnecessary hook code.
- Retire the repository-state and Markdown-health hooks entirely. Resolve checked-in and installed-copy cleanup, tests, documentation, and remaining Git safety guidance before implementation.
- Keep user-visible hook messages at key lifecycle events across local Copilot, Gemini, and Codex, using the existing visible `load-required-skills` behavior as evidence. Decide sparse message policy without assuming every hook event displays the same field.
- Discover every high-rate event and retained handler, then plan a performance-focused code review that measures latency, including startup and notification cost where observable.
- Update affected planning docs before any implementation. Complete reopened Wayfinder tickets, then revise the entire ExecPlan and acceptance checklist. No source edit is authorized by the old milestone text.

## Current evidence and cautions

- The old [RTK Setup Warning](tickets/rtk-setup-warning.md) ticket chose pinned `dev-0.50.0-rc.451`; [RTK 0.50.0 Release Facts](tickets/rtk-050-release-facts.md) now verifies official stable assets and warning suppression. Official docs do not guarantee exit-code behavior. The observed local `rtk` still prints `No hook installed`, so do not infer the local default binary or environment already uses new suppression.
- [Provider Lifecycle Facts](tickets/provider-lifecycle-facts.md) now maps official events and message fields. Copilot progress lines, Gemini `systemMessage`, and Codex `statusMessage`/`systemMessage` differ. User-observed `load-required-skills` output does not prove every other event displays its message.
- Existing [Repository State Guardrails](tickets/repository-state-guardrails.md) and [Markdown Health Hook](tickets/markdown-health-hook.md) tickets are historical decisions. New retirement tickets supersede them. Existing README and `.agents/` hook guidance accurately describe the code still checked in; update those descriptions during implementation, not prematurely.
- The previous performance probe measured Gemini handler entry-to-completion around 6-7 ms in fresh sessions. It did not measure provider startup-to-entry. See `ExecPlan.md` milestone 12 and `.agents/memory/testing/hooks.md` for the evidence and limits.
- The previous Copilot CLI timeout probe was fail-open and did not show a native timeout message. Do not treat a visible progress line as proof that a security hook enforced a decision. See `ExecPlan.md` milestone 11.
- The previous Mac host could not execute native Windows scanner HEAD-failure validation; `pwsh` skipped that case, and `flock` was absent for the aggregate runner. Those historical gates remain open unless the revised plan explicitly retires them.
- Six merged `codex/ready-ideas-fix-*` branches remained after private worktree cleanup because the repository-state hook blocked agent-run `git branch -d`. Under `AGENTS.md`, the user must run a reviewed branch deletion directly. Do not bypass the hook or touch `codex/design-context-freshness-system`.

## Next step

Claim [Stable RTK Simplification](tickets/stable-rtk-simplification.md) in the next Wayfinder session and settle its migration and code-removal boundary with the user. Other unblocked tickets cover the two hook retirements. Resolve at most one grilling ticket per Wayfinder session. Once all new decisions close, replace paused ExecPlan sections and the Windows checklist before implementation begins.

## Verification state

Planning docs and ticket files were edited in this restart; both research tickets closed and source code and installed hooks remained unchanged. `git diff --check` and link/dependency existence checks passed after research completion. Prior code tests and live checks are historical evidence, not current revision acceptance.
