# Ready ideas planning restart handoff

## Goal and status

The user changed requirements on 2026-09-28 and invoked Wayfinder. The [map](map.md) is reopened with new tickets. The [ExecPlan](ExecPlan.md) and [Windows checklist](windows-live-check.md) are marked historical and paused as execution guides. No hook source, registration, installer, or installed user file has changed in this restart. [Stable RTK Simplification](tickets/stable-rtk-simplification.md), [Markdown Health Retirement](tickets/markdown-health-retirement.md), and [Repository OKF Hook Capabilities](tickets/repository-okf-hook-capabilities.md) are closed. The new [Repository OKF Hook](tickets/repository-okf-hook.md) and remaining retirement, lifecycle, performance, and integration tickets are open.

The prior implementation remains on `codex/ready-ideas-execplan` through `c0d9ca34`. Its six fixed-point review findings were repaired and cleared by their original reviewers. Existing repository-state and Markdown-health hooks, prerelease RTK rewrite path, and user-level installations still represent the old design. Do not claim new requirements are implemented merely because the old checks passed.

## New requirements

- Official research verified stable RTK 0.50.0 and its `RTK_SUPPRESS_HOOK_WARNING` support. Plan replacement of the pinned prerelease route and removal of unnecessary hook code.
- Retire the repository-state hook and existing user-global Markdown checker. Keep `scripts/lint-okf.py`; design a simplified repository-local OKF hook that runs after an agent turn. Resolve checked-in cleanup, tests, documentation, and remaining Git safety guidance before implementation.
- Keep user-visible hook messages at key lifecycle events across local Copilot, Gemini, and Codex, using the existing visible `load-required-skills` behavior as evidence. Decide sparse message policy without assuming every hook event displays the same field.
- Discover every high-rate event and retained handler, then plan a performance-focused code review that measures latency, including startup and notification cost where observable.
- Update affected planning docs before any implementation. Complete reopened Wayfinder tickets, then revise the entire ExecPlan and acceptance checklist. No source edit is authorized by the old milestone text.

## Current evidence and cautions

- The old [RTK Setup Warning](tickets/rtk-setup-warning.md) ticket chose pinned `dev-0.50.0-rc.451`; [RTK 0.50.0 Release Facts](tickets/rtk-050-release-facts.md) verified stable assets and warning suppression. The user upgraded this Mac's PATH RTK; `rtk --version` returned `rtk 0.50.0`. [Stable RTK Simplification](tickets/stable-rtk-simplification.md) decides that both installers will require stable RTK and manage the persistent suppression setting, preserving user config. The config change and installed-file migration have not occurred. Official docs do not guarantee exit-code behavior; verify it during implementation.
- [Provider Lifecycle Facts](tickets/provider-lifecycle-facts.md) now maps official events and message fields. Copilot progress lines, Gemini `systemMessage`, and Codex `statusMessage`/`systemMessage` differ. User-observed `load-required-skills` output does not prove every other event displays its message.
- Existing [Repository State Guardrails](tickets/repository-state-guardrails.md) and [Markdown Health Hook](tickets/markdown-health-hook.md) tickets are historical decisions. New retirement tickets supersede them. Existing README and `.agents/` hook guidance accurately describe the code still checked in; update those descriptions during implementation, not prematurely.
- The user's wording initially suggested the old Markdown Health hook ran `scripts/lint-okf.py`. Code inspection showed it uses its own workspace checker; OKF lint is independent. The user requested a new repository-only turn-end hook for OKF lint. [Repository OKF Hook Capabilities](tickets/repository-okf-hook-capabilities.md) found provider-local turn-end events, but exact installed-version and worktree behavior still needs live validation. Session-end events cannot reliably require repair.
- [Markdown Health Retirement](tickets/markdown-health-retirement.md) removes maintained global checker source and registrations. Preserve shared audit history and dedicated checker state directories. Do not delete installed old scripts or registrations automatically; document leftovers. The user accepted that another machine's old global hook may keep running until manual cleanup. This Mac has no installed old scripts, registrations, or dedicated state directories.
- The previous performance probe measured Gemini handler entry-to-completion around 6-7 ms in fresh sessions. It did not measure provider startup-to-entry. See `ExecPlan.md` milestone 12 and `.agents/memory/testing/hooks.md` for the evidence and limits.
- The previous Copilot CLI timeout probe was fail-open and did not show a native timeout message. Do not treat a visible progress line as proof that a security hook enforced a decision. See `ExecPlan.md` milestone 11.
- The previous Mac host could not execute native Windows scanner HEAD-failure validation; `pwsh` skipped that case, and `flock` was absent for the aggregate runner. Those historical gates remain open unless the revised plan explicitly retires them.
- Six merged `codex/ready-ideas-fix-*` branches remained after private worktree cleanup because the repository-state hook blocked agent-run `git branch -d`. Under `AGENTS.md`, the user must run a reviewed branch deletion directly. Do not bypass the hook or touch `codex/design-context-freshness-system`.

## Next step

Claim [Repository OKF Hook](tickets/repository-okf-hook.md), the next unblocked Wayfinder ticket, and settle its repository-only event, enforcement, audit, and validation rules with the user using the [provider capability findings](research/repository-okf-hook-capabilities/findings.md). [Repository State Retirement](tickets/repository-state-retirement.md) is also unblocked. Resolve at most one grilling ticket per Wayfinder session. Once all new decisions close, replace paused ExecPlan sections and the Windows checklist before implementation begins.

## Verification state

Planning docs and ticket files were edited in this restart; both research tickets closed and source code and installed hooks remained unchanged. `git diff --check` and link/dependency existence checks passed after research completion. Prior code tests and live checks are historical evidence, not current revision acceptance.

The prior session closed Stable RTK Simplification. This session closed Markdown Health Retirement and the delegated repository-hook capability research; added a new repository-only decision ticket and adjusted blockers. Planning changes remain uncommitted; branch `codex/ready-ideas-execplan` was one commit ahead of origin before these edits. No implementation or provider run occurred.

`rtk git diff --check` passed, and relative links plus all ticket dependency filenames resolved. The `update-agent-docs` pass found no current `.agents/` behavior to change: source and installed hooks still use the old design, while new decisions live in this planning subtree. No source tests ran for documentation-only edits.

RTK read-only inventory found the prerelease binary and matching receipt installed at `~/.agents/rtk/dev-0.50.0-rc.451/`; generated explicit-command adapters and launchers are present in this checkout but absent from installed Copilot, Gemini, and Codex hook directories. The installed Copilot and Gemini automatic forwarders byte-match this checkout and will remain. RTK 0.50.0's tagged source resolves Windows config to `%APPDATA%\rtk\config.toml`; macOS uses `~/Library/Application Support/rtk/config.toml`, which is not yet present locally. No code tests or live provider runs were executed for the new decision.
