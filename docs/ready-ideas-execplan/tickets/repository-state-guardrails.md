# Repository State Guardrails

**Type:** grilling
**Status:** closed
**Blocked By:** provider-hook-capabilities.md
**Research Dir:** none

## Question

Which guardrails should prevent agent actions from damaging `.git/` metadata or overwriting uncommitted user edits, and where can those guardrails reliably run? Decide protection for direct tool writes, arbitrary Python or PowerShell scripts, and destructive Git checkout or restore commands; state limits and the required diff review workflow.

---

## Research

[Provider CLI settings for Git-metadata protection](../research/repository-state-guardrails/provider-cli-settings.md) documents current sandbox, policy, and worktree limits for Copilot CLI, Gemini CLI, and Codex CLI.

## Resolution

The user accepted layered protection on 2026-09-23. The ExecPlan must use provider pre-tool guards and agent instructions for direct `.git` file access, recognizable script traversal or writes into Git metadata, and work-discarding Git commands. Normal Git commands remain available under each provider's existing sandbox and approval rules. The guard must resolve paths where possible and account for a worktree's `.git` pointer file, resolved Git directory, and common Git directory. It must preserve legitimate read-only Git use and explain that command-text inspection cannot see arbitrary operations performed later inside Python, PowerShell, child processes, Git hooks, or other allowed programs. Do not claim complete cross-platform protection from hooks.

Use OS-enforced path protection where the provider and platform support it and verification proves its effective scope. Codex `workspace-write` already protects `.git` and a resolved worktree Git directory, but Git commands that write metadata need approval outside that boundary. Copilot's optional local sandbox can deny metadata paths on macOS and Linux, but `deniedPaths` is unsupported on Windows; nested read-only Windows behavior and linked-worktree common-directory coverage remain unverified. Gemini has optional sandboxing without a documented Git-only writer exception. No separately privileged Git service is part of this effort.

Before any Git command that might discard local work—including checkout, restore, hard reset, clean, or an equivalent variant—the agent must show `git status`, unstaged and staged diffs for affected paths, and untracked files or a dry-run deletion list as applicable. `git diff` alone is insufficient because it omits staged and untracked changes. If the command would discard changes, require explicit user approval for that command before execution. The ExecPlan must define a provider-specific, reviewable path for approval; where a provider cannot safely convey approval to a hook, keep the command blocked and have the user run it directly. Authorization for one command does not authorize later destructive commands.

Acceptance must cover direct editor writes, recognizable shell and script attempts, worktree pointer and external Git paths, destructive Git commands with dirty tracked or untracked files, legitimate Git commands, and provider-specific fail behavior. Use automated Windows cases plus a documented live-check checklist. Test an indirect script as a known limitation rather than treating it as a pass for complete interception.
