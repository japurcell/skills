# Markdown Health Retirement

**Type:** grilling
**Status:** closed
**Blocked By:** none
**Research Dir:** none

## Question

The user has withdrawn the existing user-global, workspace-wide Markdown checker and wants a separate repository-local OKF lint hook. What is the exact retirement boundary across old checker source, generated scripts, user-global registrations, installers, tests, audit behavior, and installed user hooks? Decide how to verify that the old checker no longer runs from maintained configurations. The repository-local replacement is decided in [Repository OKF Hook](repository-okf-hook.md).

---

## Resolution

Retire the existing user-global, workspace-wide Markdown Health checker. Its canonical source is `hooks/families/markdown_health.py`; `hooks/manifest.py` generates one provider script for each of Copilot, Gemini, and Codex. Remove the family, generated outputs, manifest targets, maintained hook registrations, installer copy entries, obsolete checker tests, and outdated documentation. The maintained registrations currently cover Copilot `preToolUse`, `postToolUse`, and `agentStop`; Gemini `BeforeTool`, `AfterTool`, and `AfterAgent`; and Codex `PreToolUse`, `PostToolUse`, and `Stop`. Preserve unrelated handlers on those same events. Do not write regression tests for the deleted checker.

Keep the independent repository validator `scripts/lint-okf.py` and its tests. It currently checks `.agents/instructions/` and `.agents/memory/` when invoked separately; the retired Markdown Health hook does not call it. The user's new, narrower requirement is a repository-local hook that runs this validator after an agent run or at session end. [Repository OKF Hook](repository-okf-hook.md) will decide that hook after [Repository OKF Hook Capabilities](repository-okf-hook-capabilities.md) establishes provider facts. Do not install the new hook as a user-global replacement by default.

Preserve historical `audit.log` entries. Stop future `markdown-health` audit writes from maintained source and registrations, but do not alter shared logs. Leave dedicated `~/.copilot/hooks/markdown-health-state`, `~/.gemini/hooks/markdown-health-state`, and `~/.codex/hooks/markdown-health-state` directories untouched. Do not have installers delete old installed checker scripts or registrations. Document their possible locations and manual cleanup steps for users who want to remove them. The user accepted that an old user-global hook can continue running on another machine until someone removes it manually; this is not a migration completion gate.

Current read-only inspection found no installed Markdown Health scripts or registrations in this Mac's Copilot, Gemini, or Codex user hook paths, and none of the three dedicated state directories exists. The revised ExecPlan should verify that fresh or updated repository-maintained hook configurations no longer register the old checker, installers no longer copy it, and retained hooks still run. It must not claim that every previously installed user environment has been cleaned automatically.
