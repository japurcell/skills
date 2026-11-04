# Security hooks

- Tool Guardian must conservatively handle unknown shell syntax, sinks, and payload schemas. Do not weaken unknown-input policy to pass fixtures.
- Secret scanning runs at explicit checkpoints and publication gates. A historical clean status is not permission to publish changed content.
- Security adapters emit provider-native denial JSON at exit 0 for expected blocks, malformed input, and global exceptions. Inspection/bootstrap failures still deny in warn mode. Standalone checkpoint/gate CLIs retain documented nonzero exits; informational status adapters are outside this enforcement rule.
- Never log raw tool inputs, credential text, or complete subprocess stderr. Redact the full credential span.
- Keep bounded private capture files and platform-native descendant cleanup. Native Windows job-object behavior needs native Windows proof.
- RTK forwarding errors record status without copying unbounded subprocess diagnostics. Empty successful RTK output is a valid no-op.
- Codex uses explicit RTK commands; automatic forwarders remain Copilot/Gemini-specific.

## Classification and deployment changes

- Before changing Guardian classification or limits, read the [canonical policy](../../hooks/runtime/tool_guard_policy.py), [native-data](../../scripts/test-tool-guard-native-data.py), [shell-data](../../scripts/test-tool-guard-shell-data.py), and [limit](../../scripts/test-tool-guard-limits.py) suites. Exact schemas and budgets belong there.
- Validate exact provider shape before proving data. A proven file/patch body or literal search pattern exempts only that body; remaining arguments, wrappers, interpreter flags, nested sinks, and shared-stdout producer/consumer context remain strict. Unknown syntax, aliases, fields, types, and unresolved execution stay on the strict inspection path. Data proof does not protect future execution or arbitrary write destinations.
- Generate identical provider-local policy helpers from `hooks/runtime/tool_guard_policy.py` through `hooks/families/tool_guard.py` with explicit adapter imports. Ship each helper and entrypoint in both Codex installer lists and ownership sets; preserve missing/corrupt-helper denial. Keep unused command/language imports lazy, and measure complete-hook cost before retaining optional optimization complexity.
- Scanner helper changes must preserve required-helper bootstrap, generated assets, the neutral CLI module set, and the fixture verifier's explicit reviewed dependency closures, including historical reviewed closures. Diagnostics inventory grants no authority to copy or execute arbitrary helpers. Read the [diagnostic recovery suite](../../scripts/test-hook-diagnostic-recovery.py) and missing-helper/source-free installed cases before changing the closure.
- When installed guards reject source-supported maintenance data, inspect the installed version, use bounded patches with unmistakably fake credentials, and preserve the owner-authorized enablement state. Record source and deployed proof separately; see [scanner recovery](secret-scanner-recovery.md).
- For Windows capture changes, read the [native scanner suite](../../scripts/test-scan-secrets-windows.ps1). Preserve immediate post-return temporary-file assertions and exact provider/mode/scenario/filename attribution in failures.

- Guardian uses trusted fixed action summaries, never arbitrary matched input, in bounded diagnostics and audits. Input-limit messages retain the measured quantity, threshold and unit.
- Guardian registration remains disabled until separately authorized by the owner. Source validation does not authorize installation or re-enablement.

## End Turn boundary

- End Turn reads historical status only. It never scans, retries, repairs, requests continuation, or starts background work. Missing, stale, invalid, corrupt, or unavailable status cannot block completion; a saved clean result never authorizes publication.
- Preserve the [informational status adapter](../../hooks/families/scan_status.py) and [explicit scan/gate contract](../../README.md#explicit-secret-checks-and-git-gates). Current automatic Stop/PreToolUse secret scanning is intentionally removed; preserve active explicit scanner/gate safety.

Evidence: [canonical Guardian policy](../../hooks/runtime/tool_guard_policy.py), [bounded JSON reader](../../hooks/families/common.py), provider configuration, and [security-testing](security-testing.md), checked 2026-10-21. Recheck policy, process isolation, or capture changes.
