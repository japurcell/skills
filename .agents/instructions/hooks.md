---
coverage: Rules and conventions for repo-local Copilot plus installed Copilot and Gemini hooks under `.github/hooks/`, `.copilot/hooks/`, and `.gemini/hooks/`.
---

# Git & Gemini Hooks Conventions

Guidelines for modifying and maintaining repository hook scripts and configs under `.github/hooks/`, `.copilot/hooks/`, and `.gemini/hooks/`.

## Official References

- **GitHub Copilot hooks reference:** `https://docs.github.com/en/copilot/reference/hooks-reference`
- **VS Code GitHub Copilot hooks reference:** `https://code.visualstudio.com/docs/copilot/customization/hooks`
- **Gemini CLI hooks reference:** `https://github.com/google-gemini/gemini-cli/blob/main/docs/hooks/reference.md`
- **Gemini CLI exit-code best practices:** `https://geminicli.com/docs/hooks/best-practices/#check-exit-codes`

## Shared Runtime Rules

- **stdout discipline:** Hook scripts must keep `stdout` JSON-only. Send logs, audit lines, and debug text to `stderr` or the audit log.
- **installed-copy rule:** Run `./scripts/install.sh` before live validation because Copilot and Gemini execute installed hooks from home-directory targets.
- **executable permissions:** All shell (`.sh`) and Python (`.py`) hook scripts must have standard executable permissions (`755`) set in the source tree and verified by the test-install suite. The installer (`scripts/install.sh`) must explicitly apply `chmod 755` to all copied hooks to ensure they remain executable across runtime IDE sessions regardless of the source umask.
- **Copilot surface split:** Copilot CLI can load policy, repository, user, inline-settings, and plugin hooks, but Copilot cloud agent only reads `.github/hooks/*.json` in the cloned repo and runs them inside a Linux, non-interactive, ephemeral sandbox where only `bash` or fallback `command` entries are honored.
- **Copilot progress output:** Command hooks may emit one-line progress JSON objects on stdout during execution, but they still need exactly one final non-progress JSON document for the actual hook result.
- **Copilot fail behavior:** `userPromptTransformed` can rewrite only the transformed prompt text. Command `preToolUse` hooks fail closed on non-timeout errors, but timeouts stay fail-open.
- **VS Code compatibility:** VS Code accepts Claude and Copilot hook formats, maps Copilot lowerCamelCase event names to PascalCase, ignores Claude matcher filters, and only enables custom-agent frontmatter hooks when `chat.useCustomAgentHooks` is on.
- **Gemini precedence and trust:** Gemini merges hook config in project, user, system, then extension order; project hook trust is fingerprinted from `name` plus `command`, and changed project hooks are warned as new.
- **Gemini selection and redaction:** Multiple Gemini `BeforeToolSelection` hooks union their allowed tool sets, and environment-variable redaction is off by default unless explicitly enabled and allowlisted.
- **Separate but Unified:** Keep the `.copilot` and `.gemini` hook scripts completely separated (no cross-directory imports), but structurally unified and synchronized. Use identical helper logic where possible, parameterizing only runtime-specific variables (like default paths or environment lookups) and emitting only the specific JSON decision output expected by each hook platform.
- **Fail-closed security handlers:** Security-critical hooks (like `tool-guard.py`) MUST fail-closed. Global exception handlers MUST catch unexpected errors and emit an explicit `deny` (or `{ "continue": false }`) response. Do not use fail-open exception handlers that emit `allow` on crash, as this silently bypasses protections.
- **SQLite Trace Store:** Hook observability uses a WAL-journaled SQLite database (`observability_v1.db`) as the trace source of truth under strict `0o600` permissions.
  - **Connection and Schema Init:** Connection establishment must be fast and non-blocking, omitting write-heavy `PRAGMA journal_mode=WAL;` and `PRAGMA auto_vacuum=INCREMENTAL;` connection-scoped setups (which cause concurrency conflicts). Move these PRAGMAs to one-time database schema initialization or recovery, keeping only lightweight settings like `PRAGMA foreign_keys=ON;` and `PRAGMA synchronous=NORMAL;` during connections. Secure temporary WAL/SHM side files with strict `0o600` permissions immediately after connection.
  - **Graceful OS Fallbacks:** Avoid top-level `import fcntl` to ensure cross-platform Windows compatibility. Dynamically import `fcntl` inside lock helpers, and return `-1` to fallback gracefully if unavailable.
  - **Registry and Directory Permissions:** Write all registry JSON files with explicit `0o600` permissions, and ensure subagent registry directory (`registries/subagents`) is secured with `0o700` permissions.
  - **Telemetry and Performance:** Fast-path the payload shrinking loop by checking string length before calling high-CPU `.encode("utf-8")`. Support visited-set container tracking to handle cyclical payloads and prevent unbounded recursion crashes. Unconditionally update session `start_time_ms` with the actual event timestamp of `session_start`. Append late-arriving trace chunks directly to saved `.jsonl` transcript files if the active transcript directory was already finalized and deleted.
  - **Parent Session Sanitization:** Sanitize `parent_session_id` immediately upon extraction using `[^A-Za-z0-9_-]` to neutralize path-traversal vulnerabilities and prevent arbitrary file deletion during background retention maintenance.
  - **Temporary File Security:** Secure all `.tmp` active chunk and finalization transcript writes under `try...finally` blocks, unlinking the `.tmp` file unconditionally in the `finally` block to prevent orphaned temporary file leaks on write or serialization failures.
  - **Deterministic Finalization:** Polling loops checking for completed spans must reuse a single SQLite connection instead of recreating connections inside loops to optimize performance and prevent database lock starvation, querying at a 100ms cadence.
- **Detached Maintenance:** Run rate-limited background maintenance (rate-limited once per 24 hours per runtime using a `.maintenance_last_run` sentinel file in the runtime log directory) on startup (`session_start`) or terminal (`session_end`, `subagent_stop`) events.
  - **Sentinel Touching:** Touch and update `.maintenance_last_run` only inside the spawned background child process after it starts up successfully, avoiding race conditions where a failed spawn leaves the sentinel updated.
  - **Decoupled Transactions:** Decouple file unlinking from SQLite transactions during maintenance; read paths from database first, commit/close the transaction, safely delete files from disk, and then run a separate write transaction to delete the session rows and execute compaction `PRAGMA incremental_vacuum;`.
  - **Safe Scavenging:** Scavenge stale active transcript directories and subagent registry files only if they are older than 24 hours AND are either terminal or not in the database at all (not active), preventing premature deletions.
  - **Worker Execution:** To avoid relative import errors, launch the background worker in a completely detached Python subprocess using package-style module execution `python3 -m helpers.observability --maintenance` with `cwd` set to the scripts directory containing the `helpers` package.
- **Transcript Payload Capping:** Capping payload elements by recursively checking and shrinking large objects ensures we remain within memory limits without losing context of smaller fields.
- **Session Finalization State Machine:** Moving top-level and child sessions through explicit 'finalizing' and 'sealing' states allows deterministic merge sequencing and robust backfill linkages without races.

## Output Schemas & Exit Behavior

- **Gemini Hooks Scope:**
  - Setup errors must use: `{ "continue": false, "stopReason": ... }`
  - Validation failures must use: `{ "decision": "deny", "reason": ... }`
  - Expected hook control flow must use exit code `0`, with JSON on `stdout` driving the decision. Reserve exit code `2` for true system-block cases that should use `stderr` as the reason.
- **GitHub Hooks Scope:**
  - `agentStop` / `subagentStop` outputs must use: `{ "decision": "allow|block", "reason": ... }`
  - `postToolUse` formatting hooks should emit valid JSON only: use `{}` for no-op success, or `{ "additionalContext": ... }` when the agent should see a formatter/setup failure.
  - Expected `agentStop` and `postToolUse` control flow must exit `0` so Copilot parses `stdout` JSON. Exit code `2` is warning-only for most GitHub hook events and does not apply these decision schemas.

## Copilot and VS Code compatibility

- In `.copilot/hooks/hooks.json`, keep both `subagentStart` (CLI) and `SubagentStart` (VS Code).
- CLI responses return top-level `additionalContext`; VS Code responses return `hookSpecificOutput` plus `additionalContext`.
- Prefer `agentStop` over `subagentStop` for final-response quality validators; `subagentStop` has no matcher support in Copilot hook docs and built-in `general-purpose` agents do not emit `subagentStart` or `subagentStop`.
- Keep `SessionStart` injection path active even when `SubagentStart` exists because some VS Code `runSubagent` child sessions omit `SubagentStart`.

## Repo-specific hook gotchas

- The supported hook surface is the Python operational entrypoints and Python observability emitters.
- Keep `send-event.py` registered in every supported Copilot hook event block so observability stays complete across surfaces.
- Keep `send-event.py` registered in every supported Gemini hook event block, including the lifecycle hooks that do not currently have other operational behavior (`BeforeAgent`, `BeforeModel`, `AfterModel`, `BeforeToolSelection`, `AfterTool`, `PreCompress`) so the installed config stays fully observable.
- Source auto-ingest keeps its startup scanners separate from required-skill loading. Copilot now keeps all auto-ingest wiring repo-local under `.github/hooks/hooks.json`, with startup scanning at `.github/hooks/scripts/auto-ingest-source.py` and prompt-time plus final-response enforcement at `.github/hooks/scripts/inject-auto-ingest-context.py`. Gemini keeps both pieces repo-local in `.gemini/settings.json`: startup scanning at `$GEMINI_PROJECT_DIR/.gemini/hooks/scripts/auto-ingest.py` and prompt-time injection at `$GEMINI_PROJECT_DIR/.gemini/hooks/scripts/inject-auto-ingest-context.py`. The installer still copies `.gemini/global-settings.json` to `~/.gemini/settings.json`.
- Source auto-ingest state lives in the committed repo manifest `.agents/memory/sources/source-ingest-manifest.json`, while executable helper code stays runtime-local under each hook tree.
- Concurrency for source auto-ingest manifest operations must be fully serialized. Use a platform-agnostic file-locking helper (`ManifestLock`) that wraps the entire read, reconcile, and save sequence.
- Source auto-ingest helper files must calculate file hashes (`_read_file_hash`) by streaming content in 64KB chunks instead of loading entire files into memory.
- Wrap summary scaffolding steps inside a `try...except OSError` block to prevent permissions or disk limits from crashing hook execution.
- Use a `try...finally` block inside `save_manifest` to clean up any orphaned `.tmp` files if the write or replace operation fails.
- Keep startup scanners, prompt-time injectors, and final-response backstops aligned to the same manifest schema, summary naming contract, and pending-ingest block text so stale-source guidance matches across Copilot and Gemini turns.
- The real `/ingest-source` entry point lives in `.agents/skills/ingest-source/SKILL.md`. It processes every blocking manifest entry in one run and is the only canonical recovery path.
- Source auto-ingest hooks must log robust audit information: failures/exceptions, successful context injections with granular details on individual findings (path, state, and reason), and non-injections (distinguishing between all summaries being up to date vs no sources found) to the runtime-local audit log.
- For passive shadow logging, create shadow-log parent directory before first write and keep primary plus shadow writes inside same lock section so event ordering survives.
- Log file rotation is built into the observability write path. It supports configuration via platform-specific (`GEMINI_OBSERVABILITY_LOG_MAX_BYTES`/`COPILOT_OBSERVABILITY_LOG_MAX_BYTES`, `GEMINI_OBSERVABILITY_LOG_BACKUP_COUNT`/`COPILOT_OBSERVABILITY_LOG_BACKUP_COUNT`) and general (`OBSERVABILITY_LOG_MAX_BYTES`, `OBSERVABILITY_LOG_BACKUP_COUNT`) environment variables, falling back to 10MB/100 backups by default.
  - **Fail-open resilience:** File rotation must strictly fail-open if `os.rename` or `os.remove` raises an exception, ensuring log limits or read-locks never block hook execution. **Never overwrite or clear active logs as a fallback**; doing so permanently destroys observability history on transient I/O or permission errors.
  - **Unconditional pruning:** Pruning of stale backups must execute unconditionally and independently of the active log's size threshold to ensure lowered backup limits are enforced even when the active log is quiet.
  - **Precedence testing:** Hook test suites must explicitly cover configuration precedence (runtime-specific vars overriding generic fallbacks) to prevent silent configuration regressions.
  - **O(1) directory scanning:** Prefer pre-scanning directories for existing backups with `iterdir()` rather than sequentially iterating `.exists()` over hundreds of potential indices.
  - **No strict clamps:** Rotation configuration bounds should rely on user values; do not artificially clamp maximums, but guard against `0`-byte size configurations that would trigger infinite rotation loops.
  - **OS-agnostic locking:** Avoid importing `fcntl` at the top level or relying on POSIX-exclusive lock APIs unless cleanly guarded or stubbed out on Windows.
- When editing security-hook threat patterns or Tool Guard tests, avoid pasting raw dangerous strings directly into tool payloads; construct exact strings dynamically so active guards do not block self-edits.

## Validation route

- Run targeted checks from `.agents/memory/testing/hooks.md`.
- Distinguish repo-source proof from installed/live proof.

## Gemini-specific validator guidance

- For final-response quality validators, prefer `AfterAgent` over `AfterModel`.
- Use `prompt_response` as the text under review.
- Honor `stop_hook_active` to avoid retry loops.
