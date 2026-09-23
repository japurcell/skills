# Ready ideas ExecPlan handoff

## Goal and current state

Implement [ExecPlan](ExecPlan.md) on `codex/ready-ideas-execplan`. Its 12 milestones cover the eight former Ready problems, shared hook transport, integrated validation, and later live Copilot/VS Code and Gemini checks. All Wayfinder decision tickets in [the map](map.md) are closed. The ExecPlan records detailed commit chronology.

- Milestones 1 and 3 are accepted. Milestone 3 changed only `.gemini/GEMINI.md`, `.copilot/copilot-instructions.md`, and `.codex/AGENTS.md`, as the user requested.
- Source and local tests for milestones 2 and 4–10 are integrated. Milestone 7's in-place `.git` writer repair and milestone 6's JSON credential redaction repair are included. Milestone 10's Windows live-check procedure and validation repairs are on base at `7563f95d`. Its observability fixture repair prevents detached-maintenance cleanup races and scopes mocked subprocesses to disposable `HOME`.
- User-level Codex hooks were installed after source, temporary-home, and destination review. Eight absent maintained scripts were copied; the existing startup script matched source. The merger preserved the existing `SessionStart` handler and backed up its one-handler config. Installed event counts are `SessionStart` 1, `PreToolUse` 5, `PostToolUse` 1, `Stop` 2. Hook files match source; config mode is `0600` and scripts are executable.
- Acceptance remains open for native Windows automation, deployed Codex hook delivery and timeout, and later live milestones 11 (Copilot CLI and local VS Code) and 12 (Gemini CLI). Do not mark the full plan complete from fixture results.
- The 15 clean `ready-ideas-m*` milestone and repair worktrees and their local branches were removed after integration. Two pre-rebase milestone-10 branches required deletion after `git range-diff` confirmed their rebased replacement was integrated. No matching remote branches existed. The active `codex/ready-ideas-execplan` worktree, main checkout, and unrelated `codex/design-context-freshness-system` worktree and branch remain registered.

## Exact next steps

1. Review the installed non-managed Codex hook definitions through `/hooks`, then rerun the harmless `scripts/probe-provider-hook-delivery.py` normal and one-second timeout probes. Do not bypass provider trust. The latest read-only `codex exec` exited `0` but produced zero `PreToolUse` and `Stop` markers; probe cleanup restored the exact post-install config digest. Until delivery is observed, Codex display, denial, final-event, and timeout claims remain open.
2. Run `.github/workflows/ready-ideas-windows.yml` on native Windows once GitHub authentication or a Windows runner is available. Local `gh auth status` reports invalid authentication. macOS PowerShell runs and skipped Windows cases do not close this gate. Record each workflow step and any failure in the ExecPlan.
3. In later sessions with already installed Copilot CLI/local VS Code and Gemini CLI, complete milestones 11 and 12 using [the Windows and live-check procedure](windows-live-check.md). The user chose separate sessions rather than installing those CLIs on this Mac.
4. After any new code or configuration work, run the final agent-doc pass for that work session, update this handoff and ExecPlan, and commit synchronized docs. This session's `update-agent-docs` and `okf-authoring` pass is committed at `594e49c9`.

## Evidence and constraints

- Final combined-branch checks passed: repository-state 15, security banners 5, Gemini Tool Guardian, both observability suites, Gemini auto-ingest, OKF lint, Markdown health 17 with one native-Windows skip, explicit RTK 8, generator 24, freshness 38, Bash and PowerShell temporary-home installers, Codex hook merger, three scanner suites, delivery probe 9, runner registry 14, and Codex scanner PowerShell envelopes. Full `scripts/test-all.py` cannot start because `flock` is absent; no dependency was installed. Its standalone runner suite passes.
- Security review found and then closed two source gaps: direct in-place `sed`/`perl`/`truncate`/`install` writes to `.git` were allowed, and Tool Guardian could expose a JSON credential field in its displayed and logged excerpt. Public provider regressions now pass. No destructive command was executed during review.
- The first installed Codex probe could not initialize its state database inside the sandbox. An escalated read-only probe exited `0` but still produced no event markers. Both probes ran `cleanup`; the installed config SHA-256 remained `51ff0e3b33dd36902ad66806aacbc79c61a56fdf6a7e4c2191e9f5e0969fc51d`. This is an event-delivery gap, not a passing live check.
- User explicitly approved milestone-4 `.codex/global-hooks.json`, canonical `hooks/`, and persistent user-level Codex registrations after automatic approval review conflated that scope with milestone 3's three-file limit. Another automatic review rejected a plan checkpoint containing a credential-like example; the example was removed before commit. No new dependencies or database schemas were added.
- User chose automated native Windows tests plus a live-check checklist. Live Windows sessions are supplemental. Copilot/Gemini CLIs are absent on this Mac. The pinned RTK prerelease `dev-0.50.0-rc.451` remains beside stable terminal RTK `0.49.0`; the child-scoped launcher suppresses only the false explicit-command notice and preserves stderr and exit status.
- Custom `CODEX_HOME` hook installation remains limited: installers and registered commands use `HOME/.codex` while Codex agents can use custom `CODEX_HOME`. Copilot cloud is outside user-level hook scope; provider pre-tool hooks cannot inspect arbitrary later child-process writes.

## Resume rules

Read `.agents/memory/INDEX.md`, `ARCHITECTURE.md`, `CONVENTIONS.md`, and affected area instructions before edits. Apply `exec-plans` and `tdd` for implementation. Keep worker branches private and integrate clean worktrees by rebase and `git merge --ff-only`; conflict-prone merges use an exclusive merger worktree. Run `update-agent-docs` once at the end of a code work session and keep this handoff current before stopping.
