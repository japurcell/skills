# Repository OKF Hook

**Type:** grilling
**Status:** closed
**Blocked By:** markdown-health-retirement.md, repository-okf-hook-capabilities.md
**Research Dir:** none

## Question

The user wants a simplified Markdown Health hook scoped to this repository that runs the existing `scripts/lint-okf.py` after an agent run or at session end. Given verified provider capabilities, decide exact provider and event coverage, what paths the lint checks, how findings appear, whether they block completion, audit behavior, runtime limits, tests, and how to ensure this hook is never installed user-globally.

---

## Verified current state

The existing `scripts/lint-okf.py` validates all Markdown under `.agents/instructions/` and `.agents/memory/`. It has a JSON output mode and exit codes 0 for clean, 1 for findings, and 2 for infrastructure errors. A clean local run took about 0.11 seconds. Copilot's repository `.github/hooks/scripts/validate-stop.py` already invokes the OKF adapter at `agentStop`; `.github/hooks/hooks.json` also runs the adapter after selected tools. Gemini's repository `.gemini/settings.json` already invokes its OKF adapter at `AfterAgent` and after selected tools. Neither adapter writes an OKF audit entry. No repository `.codex/hooks.json` exists yet. Current Copilot adapter output is tested for CLI response shape, but VS Code Local compatibility is not established. See [capability research](../research/repository-okf-hook-capabilities/findings.md) for official event and trust contracts.

## Resolution

Keep and simplify the existing repository-local OKF lint integration. Its target surfaces are Copilot CLI, Gemini CLI, and Codex CLI. VS Code Local and Copilot Agent Host are outside this ticket's acceptance scope. Copilot cloud is also not a promised validation surface, even though it may read repository `.github/hooks/` files. Do not install this hook to user-global Copilot, Gemini, or Codex hook configurations.

Run `scripts/lint-okf.py` once at each agent turn's completion attempt: Copilot CLI `agentStop` through the existing `.github/hooks/scripts/validate-stop.py` coordinator, Gemini CLI `AfterAgent` through the existing project adapter, and Codex CLI `Stop` through a new repository `.codex/hooks.json` registration and repo-local adapter. Remove only the OKF lint entries from Copilot `postToolUse` and Gemini `AfterTool`; keep unrelated handlers on those events. Do not add a `SessionEnd` check for OKF because it cannot reliably require repair. Reuse the current linter and adapters where suitable rather than creating a second Markdown checker. The linter continues to validate every `.md` file beneath `.agents/instructions/` and `.agents/memory/` in this repository, including unchanged files. Its current direct run completed cleanly in about 0.11 seconds on this Mac.

When lint reports definite findings, give the agent concise file, line, rule, and rerun-command diagnostics and require one repair attempt. If findings remain at the next completion attempt, allow the final response but show unresolved findings clearly. Bound the stop loop before each provider's own limit, and keep provider-native output envelopes. Treat linter exit code 2, timeout, or malformed result as `incomplete` with a visible warning, never a pass. Keep diagnostics and serialized output bounded to avoid overflowing a hook response. The Copilot and Gemini adapters already cap diagnostics at 20 and output below 8 KiB; preserve those limits or justify a compatible change.

Carry the user's audit requirement into this repository hook. Write one provider-convention `audit.log` entry per turn-end validation attempt, with `pass`, `fail`, or `incomplete`, checked file count, finding count, event/session context when available, and a sorted, sanitized list of workspace-relative checked paths. Cap each physical line at 4 KiB and include omitted-path count when needed. Never log document contents or diagnostic text. A repaired continuation can produce its own next completion-attempt entry; avoid duplicate entries for identical repeated stop events. If the audit write fails, report audit unavailability without changing a definite lint result. This is the only audit behavior needed for OKF lint; post-tool OKF audit entries disappear with those invocations.

Keep the current repository validator and its independent tests. Update targeted hook tests for turn-end pass, finding, incomplete result, one bounded repair attempt, audit record and failure, path cap, repo-only registration, and absence of OKF post-tool entries. Test provider-native CLI envelopes, nested worktree paths, and Windows command resolution. Verify current installed CLI versions and hook trust with live local Copilot, Gemini, and Codex runs before claiming deployed coverage; Windows acceptance remains automated checks plus a documented live-check checklist. Include a no-global-copy assertion for installers, especially because `.codex/` also contains user-global hook sources. Do not add regression tests for the retired workspace-wide Markdown checker.
