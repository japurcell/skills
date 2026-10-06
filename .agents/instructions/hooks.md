---
type: Agent Instruction
description: Rules for Codex, Copilot, and Gemini hook sources and installed behavior
---

# Agent Hook Conventions

Guidelines for modifying and maintaining repository hook scripts and configs under `.github/hooks/`, `.copilot/hooks/`, `.gemini/hooks/`, and `.codex/hooks/`.

For source auto-ingest scanners, injectors, manifests, or pending gates, read [Hook Auto-Ingest Rules](hooks-auto-ingest.md). Skip it for other hook work. For observability emitters, trace storage, transcript finalization, logging, or maintenance, read [Hook Observability Rules](hooks-observability.md). Skip it for operational hook changes.

## Official References

- **GitHub Copilot hooks reference:** `https://docs.github.com/en/copilot/reference/hooks-reference`
- **VS Code harness selection and Local hooks:** `https://code.visualstudio.com/docs/agent-customization/hooks`
- **VS Code Local hook schemas:** `https://code.visualstudio.com/docs/agents/reference/hooks-reference`
- **Gemini CLI hooks reference:** `https://github.com/google-gemini/gemini-cli/blob/main/docs/hooks/reference.md`
- **Gemini CLI exit-code best practices:** `https://geminicli.com/docs/hooks/best-practices/#check-exit-codes`
- **Codex hooks:** `https://learn.chatgpt.com/docs/hooks`

## Shared Runtime Rules

- **sparse lifecycle messages:** Local CLI startup and turn-end operational hooks report a short hook-name, outcome, and safe count where useful. Copilot uses one progress JSON line before its final JSON for an allowed visible result; Gemini and Codex use `systemMessage`. Put a blocked result in the existing native denial reason without a second display. Every stop attempt, including a repair retry, reports an outcome. Ordinary pass messages contain no path, command, document content, or secret. Keep high-rate tool passes, observability-only hooks, SessionEnd success, and the completion bell free of text messages. Actionable tool blocks, warnings, and incomplete scans remain immediate. Do not add per-call RTK audit records to prove a pass.

- **generated-provider ownership:** Provider-local Python files with a `Generated from hooks/families/...` header are build outputs. Edit their canonical `hooks/families/` renderer or its typed provider metadata, run `python3 scripts/generate-hooks.py --write`, then require `python3 scripts/generate-hooks.py --check` before committing. Both installers run the same read-only check before destination mutation; stale output must stop installation with the `--write` recovery command, while generator failure must stop without write advice. Never add cross-provider runtime imports; installers never invoke generator write mode.
- **agent-brain candidate adapters:** Render provider entrypoints and packaged `skills/agent-brain/assets/adapters/` together; consumers copy the runnable bundle without the generator. Keep registration templates inactive and preserve unrelated hooks. Load [native adapter contracts](../../skills/agent-brain/references/native-adapters.md) before changing native envelopes, cumulative watchdogs, pinned input handling, foreground admission or output settlement. Offline translation is never deployed provider certification.
- **raw-source authority:** For exact hook behavior questions or changes (visible CLI output, stdout parsing, progress messages, event timing, matcher behavior, or output schemas), read the matching raw source under `.agents/sources/` after the summary. Summary files route the investigation but are not final authority for precise hook behavior.
- **stdout discipline:** Hook scripts must keep `stdout` JSON-only. Send logs, audit lines, and debug text to `stderr` or the audit log.
- **installed-copy rule:** Run `./scripts/install.sh` before live validation because Codex, Copilot, and Gemini execute installed hooks from home-directory targets.
- **runtime-log isolation:** Installers must not copy ignored runtime state from source hook trees, especially `.gemini/hooks/logs/`. Preserve existing destination logs while copying maintained hook scripts and config.
- **stdin completion:** Hook JSON readers must return after one complete JSON value is available instead of waiting for stdin EOF. Read pipe bytes incrementally, drain bytes already buffered after the value, and reject any non-whitespace trailing data. Open pipes need a bounded completion window before the first byte and after every incomplete chunk because malformed and valid prefixes cannot always be distinguished syntactically. Keep the Windows path compatible with Python versions before 3.12 by using `PeekNamedPipe` instead of relying on nonblocking pipe support in `os.set_blocking`.
- **RTK failure diagnostics:** When an RTK forwarder receives a nonzero subprocess exit, audit the exit code without copying subprocess stderr. RTK stderr can contain payload or environment details and has no wrapper-defined size bound.
- **Scanner Git waits:** Let a fast Git child wake the scanner immediately with bounded `Popen.wait(timeout=...)`. Keep deadline and captured-output checks on each wait cycle, and keep descendant-process verification after the parent exits. An unconditional polling sleep adds one full interval to each of several Git calls in a clean scan.
- **Explicit RTK commands:** Use stable RTK 0.50.0 or newer directly. The installers persist `[hooks] suppress_hook_warning = true` in the user's RTK TOML without changing unrelated settings; this account-wide setting silences only the false missing-hook advisory. Keep the Copilot and Gemini automatic RTK forwarders and their provider registrations. Codex uses explicit `rtk` commands and has no automatic RTK forwarder.
- **executable permissions:** All shell (`.sh`) and Python (`.py`) hook scripts must have standard executable permissions (`755`) set in the source tree and verified by the test-install suite. The installer (`scripts/install.sh`) must explicitly apply `chmod 755` to all copied hooks to ensure they remain executable across runtime IDE sessions regardless of the source umask.
- **Copilot surface split:** Copilot CLI can load policy, repository, user, inline-settings, and plugin hooks, but Copilot cloud agent only reads `.github/hooks/*.json` in the cloned repo and runs them inside a Linux, non-interactive, ephemeral sandbox where only `bash` or fallback `command` entries are honored.
- **Copilot progress output:** Command hooks may emit one-line progress JSON objects on stdout during execution, but they still need exactly one final non-progress JSON document for the actual hook result.
- **Copilot post-tool event split:** `postToolUse` fires only after successful tool completion. Handle failed tools through `postToolUseFailure`, whose output can add recovery context but cannot retroactively block or undo the failed tool.
- **Copilot stop-loop bound:** Keep stop validators bounded and idempotent. For `agentStop`, use `stop_hook_active` to detect a turn already forced by a prior block and self-limit before Copilot's eight-consecutive-block runaway guard overrides the hook.
- **Copilot required-skill announcement:** `.copilot/hooks/scripts/load-required-skills.py` emits a display-only progress message, `Required skill context loaded from N file(s).`, before its final `additionalContext` JSON for Copilot CLI-shaped payloads when required skills load. Supported progress payloads have no event name or a lowerCamelCase event name such as `sessionStart` or `subagentStart`; VS Code-compatible PascalCase events keep stdout to one final JSON object.
- **Copilot fail behavior:** `userPromptTransformed` can rewrite only the transformed prompt text. Command `preToolUse` hooks fail closed on non-timeout errors, but timeouts stay fail-open. For block-mode policy denials, emit structured deny JSON and exit `0` so Copilot surfaces `permissionDecisionReason` instead of only generic failure output.
- **VS Code compatibility:** Identify the selected harness before applying hook contracts. Local accepts Claude and Copilot formats, maps Copilot lowerCamelCase events to PascalCase, ignores Claude matcher filters, and requires `chat.useCustomAgentHooks` for custom-agent frontmatter hooks. Copilot Agent Host uses the shared Copilot CLI/SDK contract; verify event availability in the deployed version.
- **Gemini precedence and trust:** Gemini merges hook config in project, user, system, then extension order; project hook trust is fingerprinted from `name` plus `command`, and changed project hooks are warned as new.
- **Gemini selection and redaction:** Multiple Gemini `BeforeToolSelection` hooks union their allowed tool sets, and environment-variable redaction is off by default unless explicitly enabled and allowlisted.
- **Separate but Unified:** Keep the `.copilot` and `.gemini` hook scripts completely separated (no cross-directory imports), but structurally unified and synchronized. Use identical helper logic where possible, parameterizing only runtime-specific variables (like default paths or environment lookups) and emitting only the specific JSON decision output expected by each hook platform.
- **Codex required skills:** Keep `.codex/global-hooks.json` inactive in the repository and merge its maintained `SessionStart`, `PreToolUse`, and `Stop` groups into user-global `~/.codex/hooks.json`. The hook must emit one JSON document, use `hookSpecificOutput.additionalContext`, announce the loaded-file count through `systemMessage`, fail closed with `continue: false`, and never import another runtime's hook code.
- **Codex size and audit boundaries:** Bound raw required-skill files independently from the final stripped-and-wrapped context so large removable YAML frontmatter does not consume the injection budget. Audit paths must reject symbolic links, Windows junctions, and other reparse points before opening or changing permissions.
- **Codex trust:** Non-managed Codex hooks must be reviewed after installation or definition changes through `/hooks`; never advise bypassing hook trust.
- **Codex install safety:** The shared merger must preserve unrelated hook data, replace only exact maintained POSIX or Windows commands, reject symlinked config destinations, back up only real semantic changes, and atomically write owner-only JSON. Bash and PowerShell installers must refuse a linked installed-hook destination instead of following it.
- **Codex registered-hook deployment:** When `.codex/global-hooks.json` gains a maintained handler, add its script and any local launcher it invokes to both installers' exact Codex copy lists and the merger's owned-file list. Temporary-home installer tests must resolve the registered command to an installed file and verify its launcher is installed too.
- **Fail-closed security handlers:** Security-critical hooks (like `tool-guard.py` and `scan-secrets.py`) MUST fail-closed. Global exception handlers and malformed-input paths must exit `0` after emitting the runtime-specific denial JSON; Gemini must not use warning exit `1` for block-mode failures. Do not use fail-open exception handlers that emit `allow` on crash, as this silently bypasses protections.
- **Security banners:** Tool Guardian block and warning decisions name the safe tool/action, show at most three distinct category/severity/rule causes with an omitted count, and show one redacted `Action:` excerpt with the matched operation first and a 160-character cap. Input-limit causes report the actual threshold, measured count, and unit; only a trusted known provider field may be named. Input limits and inspection failures stay fail-closed and never suggest `TOOL_GUARD_ALLOWLIST`. Redact complete quoted credential values, including spaces, before truncation. Never trust a matched span or full tool input as safe context: summarize credential-bearing operations from allowlisted fields and omit uncertain context. Its guard log stores the same safe rule metadata and exact excerpt, never raw input. Scanner findings and incomplete scans use action-named `scan-secrets blocked` or `scan-secrets warning` messages without matched values or file contents. Codex registers both checks under `PreToolUse`; scanner also runs at `Stop`.
- **Secret scanner Git capture:** Canonical `hooks/families/scan_secrets.py` captures Git stdout in an owner-only temporary regular file, not a pipe. A timeout, oversized or malformed output, unexpected Git failure, or open descendant-held output handle is an incomplete scan: discard partial bytes, deny in block mode, and emit a safe action-named warning in warn mode. A nonzero `rev-parse --verify HEAD` identifies an unborn branch only after an independent symbolic-branch and missing-ref check; other HEAD failures are incomplete scans. Keep cleanup bounded and never copy raw Git output into responses or logs.

## Output Schemas & Exit Behavior

- **Gemini Hooks Scope:**
  - Setup errors must use: `{ "continue": false, "stopReason": ... }`
  - Validation failures must use: `{ "decision": "deny", "reason": ... }`
  - Expected hook control flow must use exit code `0`, with JSON on `stdout` driving the decision. Reserve exit code `2` for true system-block cases that should use `stderr` as the reason.
- **GitHub Hooks Scope:**
  - `agentStop` / `subagentStop` outputs must use: `{ "decision": "allow|block", "reason": ... }`
  - `postToolUse` formatting hooks should emit valid JSON only: use `{}` for no-op success, or `{ "additionalContext": ... }` when the agent should see a formatter/setup failure.
  - Copilot CLI command `preToolUse` uses top-level `permissionDecision` (`allow`, `deny`, or `ask`) and `modifiedArgs` for rewritten tool arguments. VS Code Local `PreToolUse` uses event-specific `hookSpecificOutput.permissionDecision` and `hookSpecificOutput.updatedInput`. Verify the harness, event format, and deployed schema before changing an existing adapter.
  - Expected `agentStop` and `postToolUse` control flow must exit `0` so Copilot parses `stdout` JSON. Exit code `2` is warning-only for most GitHub hook events and does not apply these decision schemas.

## Repository OKF validation hooks

- Keep `scripts/lint-okf.py` as the only OKF profile authority. The repo-local adapters under `.github/hooks/scripts/lint-okf.py` and `.gemini/hooks/scripts/lint-okf.py` translate its JSON diagnostics into provider envelopes and must not duplicate document rules.
- Run OKF only at turn end: Copilot `agentStop`/`subagentStop` through `validate-stop.py`, Gemini `AfterAgent`, and Codex project-local `Stop` through `.codex/hooks.json`. Keep this registration out of user-global hook templates and installer copy lists. Resolve the Codex command from the Git root because Codex runs it with the session working directory, which may be nested.
- Anchor adapter execution to the checkout containing the adapter. Normalize the payload `cwd`, require it to remain inside that checkout, allow nested checkout paths, and never execute a linter selected from an external payload path.
- Run the central linter with `sys.executable`, argument-list subprocess execution, and an 8-second timeout inside the providers' 10-second hook timeout. Translate malformed input, missing runtime files, invalid linter JSON, exit `2`, timeouts, and unexpected exceptions to provider-valid `OKF900` output with exit `0`.
- Preserve central diagnostic order by `path`, `line`, `column`, then ID. Show no more than 20 findings, include the omitted count and platform-specific rerun command, and measure the final JSON-encoded provider response when enforcing the 8 KiB output limit.
- Give definite findings one repair attempt. A repeated stop with `stop_hook_active` permits completion and surfaces unresolved findings. Infrastructure failure is `incomplete` with a visible `OKF900` warning, not a clean pass or an unbounded stop loop. Copilot's coordinator preserves source-ingest-first blocking independently of OKF's allowed incomplete response.
- Audit each nonempty turn-end validation batch in the provider's `audit.log`: outcome, checked and finding counts, attempt, hashed session context, and sorted workspace-relative paths only. Keep each physical line at most 4 KiB with an omitted-path count; suppress identical repeats but record a repair retry separately. Audit-write failure warns without changing the lint decision.

## Copilot and VS Code compatibility

- On Windows systems, Copilot hooks config (e.g. `hooks.json` and `rtk-rewrite.json`) must explicitly define both `"bash"` (Unix) and `"powershell"` (Windows) keys for command hooks to execute natively and in VS Code on Windows.
- In `.copilot/hooks/hooks.json`, keep both `subagentStart` (CLI) and `SubagentStart` (VS Code Local).
- Copilot CLI and Copilot Agent Host use the shared Copilot output contract. VS Code Local uses event-specific `hookSpecificOutput` for context and decisions; verify the event schema rather than inferring it from the VS Code product name.
- Prefer `agentStop` over `subagentStop` for final-response quality validators; `subagentStop` has no matcher support in Copilot hook docs and built-in `general-purpose` agents do not emit `subagentStart` or `subagentStop`.
- Keep `SessionStart` injection path active even when `SubagentStart` exists because some VS Code `runSubagent` child sessions omit `SubagentStart`.

## Repo-specific hook gotchas

- The supported operational surface uses Python entry points. Load the focused auto-ingest or observability rules above before changing those subsystems.
- When editing security-hook threat patterns or Tool Guard tests, avoid pasting raw dangerous strings directly into tool payloads; construct exact strings dynamically so active guards do not block self-edits.

## Validation route

- Run targeted checks from `.agents/memory/testing/hooks.md`.
- Distinguish repo-source proof from installed/live proof.

## Gemini-specific validator guidance

- For final-response quality validators, prefer `AfterAgent` over `AfterModel`.
- Use `prompt_response` as the text under review.
- Honor `stop_hook_active` to avoid retry loops.
