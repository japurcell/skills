---
type: Agent Instruction
description: Rules for Codex, Copilot, and Gemini hook sources and installed behavior
---

# Agent Hook Conventions

Guidelines for modifying and maintaining repository hook scripts and configs under `.github/hooks/`, `.copilot/hooks/`, `.gemini/hooks/`, and `.codex/hooks/`.

For source auto-ingest scanners, injectors, manifests, or pending gates, read [Hook Auto-Ingest Rules](hooks-auto-ingest.md). Skip it for other hook work. For observability emitters, trace storage, transcript finalization, logging, or maintenance, read [Hook Observability Rules](hooks-observability.md). Skip it for operational hook changes.

## Official References

- **GitHub Copilot hooks reference:** `https://docs.github.com/en/copilot/reference/hooks-reference`
- **VS Code GitHub Copilot hooks reference:** `https://code.visualstudio.com/docs/copilot/customization/hooks`
- **Gemini CLI hooks reference:** `https://github.com/google-gemini/gemini-cli/blob/main/docs/hooks/reference.md`
- **Gemini CLI exit-code best practices:** `https://geminicli.com/docs/hooks/best-practices/#check-exit-codes`
- **Codex hooks:** `https://learn.chatgpt.com/docs/hooks`

## Shared Runtime Rules

- **generated-provider ownership:** Provider-local Python files with a `Generated from hooks/families/...` header are build outputs. Edit their canonical `hooks/families/` renderer or its typed provider metadata, run `python3 scripts/generate-hooks.py --write`, then require `python3 scripts/generate-hooks.py --check` before committing. Both installers run the same read-only check before destination mutation; stale output must stop installation with the `--write` recovery command, while generator failure must stop without write advice. Never add cross-provider runtime imports; installers never invoke generator write mode.
- **raw-source authority:** For exact hook behavior questions or changes (visible CLI output, stdout parsing, progress messages, event timing, matcher behavior, or output schemas), read the matching raw source under `.agents/sources/` after the summary. Summary files route the investigation but are not final authority for precise hook behavior.
- **stdout discipline:** Hook scripts must keep `stdout` JSON-only. Send logs, audit lines, and debug text to `stderr` or the audit log.
- **installed-copy rule:** Run `./scripts/install.sh` before live validation because Codex, Copilot, and Gemini execute installed hooks from home-directory targets.
- **runtime-log isolation:** Installers must not copy ignored runtime state from source hook trees, especially `.gemini/hooks/logs/`. Preserve existing destination logs while copying maintained hook scripts and config.
- **stdin completion:** Hook JSON readers must return after one complete JSON value is available instead of waiting for stdin EOF. Read pipe bytes incrementally, drain bytes already buffered after the value, and reject any non-whitespace trailing data. Open pipes need a bounded completion window before the first byte and after every incomplete chunk because malformed and valid prefixes cannot always be distinguished syntactically. Keep the Windows path compatible with Python versions before 3.12 by using `PeekNamedPipe` instead of relying on nonblocking pipe support in `os.set_blocking`.
- **RTK failure diagnostics:** When an RTK forwarder receives a nonzero subprocess exit, audit the exit code without copying subprocess stderr. RTK stderr can contain payload or environment details and has no wrapper-defined size bound.
- **Explicit RTK commands:** `hooks/families/rtk.py` also renders provider-local explicit-command adapters and launchers. The adapters rewrite only a safely parsed shell executable token after a receipt-backed, checksum-verified `dev-0.50.0-rc.451` install; unsafe syntax and unsupported tools remain unchanged. The launcher sets `RTK_SUPPRESS_HOOK_WARNING=1` only for the child and forwards its arguments, streams, and exit code. Do not filter stderr, change stable terminal RTK, or use the prerelease binary's `--version` as provenance.
- **executable permissions:** All shell (`.sh`) and Python (`.py`) hook scripts must have standard executable permissions (`755`) set in the source tree and verified by the test-install suite. The installer (`scripts/install.sh`) must explicitly apply `chmod 755` to all copied hooks to ensure they remain executable across runtime IDE sessions regardless of the source umask.
- **Copilot surface split:** Copilot CLI can load policy, repository, user, inline-settings, and plugin hooks, but Copilot cloud agent only reads `.github/hooks/*.json` in the cloned repo and runs them inside a Linux, non-interactive, ephemeral sandbox where only `bash` or fallback `command` entries are honored.
- **Copilot progress output:** Command hooks may emit one-line progress JSON objects on stdout during execution, but they still need exactly one final non-progress JSON document for the actual hook result.
- **Copilot post-tool event split:** `postToolUse` fires only after successful tool completion. Handle failed tools through `postToolUseFailure`, whose output can add recovery context but cannot retroactively block or undo the failed tool.
- **Copilot stop-loop bound:** Keep stop validators bounded and idempotent. For `agentStop`, use `stop_hook_active` to detect a turn already forced by a prior block and self-limit before Copilot's eight-consecutive-block runaway guard overrides the hook.
- **Copilot required-skill announcement:** `.copilot/hooks/scripts/load-required-skills.py` emits a display-only progress message, `Required skill context loaded from N file(s).`, before its final `additionalContext` JSON for Copilot CLI-shaped payloads when required skills load. Supported progress payloads have no event name or a lowerCamelCase event name such as `sessionStart` or `subagentStart`; VS Code-compatible PascalCase events keep stdout to one final JSON object.
- **Copilot fail behavior:** `userPromptTransformed` can rewrite only the transformed prompt text. Command `preToolUse` hooks fail closed on non-timeout errors, but timeouts stay fail-open. For block-mode policy denials, emit structured deny JSON and exit `0` so Copilot surfaces `permissionDecisionReason` instead of only generic failure output.
- **VS Code compatibility:** VS Code accepts Claude and Copilot hook formats, maps Copilot lowerCamelCase event names to PascalCase, ignores Claude matcher filters, and only enables custom-agent frontmatter hooks when `chat.useCustomAgentHooks` is on.
- **Gemini precedence and trust:** Gemini merges hook config in project, user, system, then extension order; project hook trust is fingerprinted from `name` plus `command`, and changed project hooks are warned as new.
- **Gemini selection and redaction:** Multiple Gemini `BeforeToolSelection` hooks union their allowed tool sets, and environment-variable redaction is off by default unless explicitly enabled and allowlisted.
- **Separate but Unified:** Keep the `.copilot` and `.gemini` hook scripts completely separated (no cross-directory imports), but structurally unified and synchronized. Use identical helper logic where possible, parameterizing only runtime-specific variables (like default paths or environment lookups) and emitting only the specific JSON decision output expected by each hook platform.
- **Codex required skills:** Keep `.codex/global-hooks.json` inactive in the repository and merge its maintained `SessionStart`, `PreToolUse`, and `Stop` groups into user-global `~/.codex/hooks.json`. The hook must emit one JSON document, use `hookSpecificOutput.additionalContext`, announce the loaded-file count through `systemMessage`, fail closed with `continue: false`, and never import another runtime's hook code.
- **Codex size and audit boundaries:** Bound raw required-skill files independently from the final stripped-and-wrapped context so large removable YAML frontmatter does not consume the injection budget. Audit paths must reject symbolic links, Windows junctions, and other reparse points before opening or changing permissions.
- **Codex trust:** Non-managed Codex hooks must be reviewed after installation or definition changes through `/hooks`; never advise bypassing hook trust.
- **Codex install safety:** The shared merger must preserve unrelated hook data, replace only exact maintained POSIX or Windows commands, reject symlinked config destinations, back up only real semantic changes, and atomically write owner-only JSON. Bash and PowerShell installers must refuse a linked installed-hook destination instead of following it.
- **Codex registered-hook deployment:** When `.codex/global-hooks.json` gains a maintained handler, add its script and any local launcher it invokes to both installers' exact Codex copy lists and the merger's owned-file list. Temporary-home installer tests must resolve the registered command to an installed file and verify its launcher is installed too.
- **Repository-state guard:** `hooks/families/repository_state.py` generates self-contained Copilot, Gemini, and Codex pre-tool guards. Direct editor targets are checked against the workspace `.git` entry, resolved Git directory, and common Git directory; literal shell/script metadata writes and work-discarding Git verbs are denied. A blocked checkout, restore, reset, clean, or equivalent command stays blocked until the user runs the exact command after status, unstaged and staged diff, and untracked/dry-run review. No provider approval route has been proved to bind one reviewed command to one user decision. Do not infer approval from prose. Read-only Git commands remain available. Arbitrary later writes in Python, PowerShell, child processes, or Git hooks are outside text inspection. Copilot command-hook timeouts remain fail-open, so hook denials alone are not an OS-level protection boundary.
- **Fail-closed security handlers:** Security-critical hooks (like `tool-guard.py` and `scan-secrets.py`) MUST fail-closed. Global exception handlers and malformed-input paths must exit `0` after emitting the runtime-specific denial JSON; Gemini must not use warning exit `1` for block-mode failures. Do not use fail-open exception handlers that emit `allow` on crash, as this silently bypasses protections.
- **Security banners:** Tool Guardian block and warning decisions name the safe tool/action, show at most three category/severity pairs, and show one redacted `Action:` excerpt with the matched operation first and a 160-character cap. Redact complete quoted credential values, including spaces, before truncation. Its guard log stores that exact excerpt with threat metadata, never raw input. Scanner findings and incomplete scans use action-named `scan-secrets blocked` or `scan-secrets warning` messages without matched values or file contents. Codex registers both checks under `PreToolUse`; scanner also runs at `Stop`.
- **Secret scanner Git capture:** Canonical `hooks/families/scan_secrets.py` captures Git stdout in an owner-only temporary regular file, not a pipe. A timeout, oversized or malformed output, unexpected Git failure, or open descendant-held output handle is an incomplete scan: discard partial bytes, deny in block mode, and emit a safe action-named warning in warn mode. Only `rev-parse --verify HEAD` may use its expected nonzero result to identify a repository without HEAD. Keep cleanup bounded and never copy raw Git output into responses or logs.
- **Markdown health ownership:** Edit `hooks/families/markdown_health.py`, then regenerate the three provider scripts. Its pre-tool baseline and post/final events share per-session, per-workspace state. Snapshot only paths and metadata for untouched Markdown; read and fingerprint content only for touched candidates. Missing, stale, or oversized state must surface `incomplete`, never a clean pass. Keep audit records to one bounded line per nonempty batch and omit document content and link targets.

## Output Schemas & Exit Behavior

- **Gemini Hooks Scope:**
  - Setup errors must use: `{ "continue": false, "stopReason": ... }`
  - Validation failures must use: `{ "decision": "deny", "reason": ... }`
  - Expected hook control flow must use exit code `0`, with JSON on `stdout` driving the decision. Reserve exit code `2` for true system-block cases that should use `stderr` as the reason.
- **GitHub Hooks Scope:**
  - `agentStop` / `subagentStop` outputs must use: `{ "decision": "allow|block", "reason": ... }`
  - `postToolUse` formatting hooks should emit valid JSON only: use `{}` for no-op success, or `{ "additionalContext": ... }` when the agent should see a formatter/setup failure.
  - `preToolUse` / `PreToolUse` command hooks can control tool execution via `"permissionDecision"`. Set to `"ask"` to trigger a manual interactive confirmation dialog in Copilot CLI, or set to `"allow"` to silently execute the tool call or rewritten `updatedInput` without prompts.
  - Expected `agentStop` and `postToolUse` control flow must exit `0` so Copilot parses `stdout` JSON. Exit code `2` is warning-only for most GitHub hook events and does not apply these decision schemas.

## Repository OKF validation hooks

- Keep `scripts/lint-okf.py` as the only OKF profile authority. The repo-local adapters under `.github/hooks/scripts/lint-okf.py` and `.gemini/hooks/scripts/lint-okf.py` translate its JSON diagnostics into provider envelopes and must not duplicate document rules.
- Anchor adapter execution to the checkout containing the adapter. Normalize the payload `cwd`, require it to remain inside that checkout, allow nested checkout paths, and never execute a linter selected from an external payload path.
- Run the central linter with `sys.executable`, argument-list subprocess execution, and an 8-second timeout inside the providers' 10-second hook timeout. Translate malformed input, missing runtime files, invalid linter JSON, exit `2`, timeouts, and unexpected exceptions to provider-valid `OKF900` output with exit `0`.
- Preserve central diagnostic order by `path`, `line`, `column`, then ID. Show no more than 20 findings, include the omitted count and platform-specific rerun command, and measure the final JSON-encoded provider response when enforcing the 8 KiB output limit.
- Native camelCase Copilot payloads do not carry an event-name field. Detect `postToolUse` from its documented `toolName` shape; eventless stop payloads use the common stop decision envelope. Continue to honor explicit VS Code-compatible `PostToolUse`, `Stop`, and `SubagentStop` event names.
- Keep source ingest first on Copilot `agentStop` and `subagentStop` and in Gemini's sequential `AfterAgent` group. Register OKF immediate feedback only for the accepted Copilot `bash|powershell|create|edit` and Gemini `write_file|replace|run_shell_command` matchers.

## Copilot and VS Code compatibility

- On Windows systems, Copilot hooks config (e.g. `hooks.json` and `rtk-rewrite.json`) must explicitly define both `"bash"` (Unix) and `"powershell"` (Windows) keys for command hooks to execute natively and in VS Code on Windows.
- In `.copilot/hooks/hooks.json`, keep both `subagentStart` (CLI) and `SubagentStart` (VS Code).
- CLI responses return top-level `additionalContext`; VS Code responses return `hookSpecificOutput` plus `additionalContext`.
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
