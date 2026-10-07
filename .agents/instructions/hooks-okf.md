---
type: Agent Instruction
description: Repository-only OKF adapters, bounded diagnostics, and final-response behavior.
---

# Repository OKF Hooks

- Keep `scripts/lint-okf.py` as the only OKF profile authority. The repo-local adapters under `.github/hooks/scripts/lint-okf.py` and `.gemini/hooks/scripts/lint-okf.py` translate its JSON diagnostics into provider envelopes and must not duplicate document rules.
- Run OKF only at turn end: Copilot `agentStop`/`subagentStop` through `validate-stop.py`, Gemini `AfterAgent`, and Codex project-local `Stop` through `.codex/hooks.json`. Keep this registration out of user-global hook templates and installer copy lists. Resolve the Codex command from the Git root because Codex runs it with the session working directory, which may be nested.
- Anchor adapter execution to the checkout containing the adapter. Normalize the payload `cwd`, require it to remain inside that checkout, allow nested checkout paths, and never execute a linter selected from an external payload path.
- Run the central linter with `sys.executable`, argument-list subprocess execution, and an 8-second timeout inside the providers' 10-second hook timeout. Translate malformed input, missing runtime files, invalid linter JSON, exit `2`, timeouts, and unexpected exceptions to provider-valid `OKF900` output with exit `0`.
- Preserve central diagnostic order by `path`, `line`, `column`, then ID. Show no more than 20 findings, include the omitted count and platform-specific rerun command, and measure the final JSON-encoded provider response when enforcing the 8 KiB output limit.
- Give definite findings one repair attempt. A repeated stop with `stop_hook_active` permits completion and surfaces unresolved findings. Infrastructure failure is `incomplete` with a visible `OKF900` warning, not a clean pass or an unbounded stop loop. Copilot's coordinator preserves source-ingest-first blocking independently of OKF's allowed incomplete response.
- Audit each nonempty turn-end validation batch in the provider's `audit.log`: outcome, checked and finding counts, attempt, hashed session context, and sorted workspace-relative paths only. Keep each physical line at most 4 KiB with an omitted-path count; suppress identical repeats but record a repair retry separately. Audit-write failure warns without changing the lint decision.

For validation, use [hook testing](testing/hooks.md) and the [source-ingestion cases](testing/hooks-auto-ingest.md) when coordinator ordering changes.
