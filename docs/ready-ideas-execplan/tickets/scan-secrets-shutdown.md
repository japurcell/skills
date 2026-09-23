# Scan Secrets Shutdown

**Type:** grilling
**Status:** closed
**Blocked By:** none
**Research Dir:** none

## Question

What bounded subprocess behavior should replace or repair scan-secrets shutdown's threaded Git reader, and how should timeout, partial output, and failure affect secret detection across providers and platforms? Establish a regression scenario matching the observed Windows hang.

---

## Resolution

The user accepted all three recommendations on 2026-09-23. Replace the threaded pipe reader in canonical `hooks/families/scan_secrets.py` with file-backed Git output capture. Start Git with an argument list and stdout redirected to a securely created temporary file; do not use `stdout=PIPE` or `subprocess.run(capture_output=True)`. Poll for child exit, the existing five-second per-command deadline (bounded by the eight-second whole-scan deadline), and the existing 8 MiB accepted-output limit. Stop the child on timeout or excess output with bounded cleanup, read no more than the accepted limit into memory after successful exit, and remove the temporary file on every path. Keep `GIT_TERMINAL_PROMPT=0`, empty `GIT_ASKPASS`, literal pathspecs, hidden Git stderr, and POSIX process-group cleanup. Windows cleanup must never wait for pipe EOF or join a reader thread. Process creation may outlast a Python timeout; describe that platform limit rather than promise an absolute wall-clock bound.

Treat timeout, over-limit output, failed Git commands, malformed or incomplete output, and temporary-file errors as **incomplete scans**. Discard all partial Git output; never infer a clean scan or findings from it. Preserve the intentional `git rev-parse --verify HEAD` nonzero result that means a repository has no HEAD. In pre-tool block mode, emit the provider's structured denial with exit `0`. In session-end warn mode, emit a safe, native `scan-secrets warning` that says the scan was incomplete and names the action, without changing execution. Do not show Git output, secret values, or partial matches. This warning is distinct from the generic potential-secret finding banner selected in [Security Hook Notifications](security-hook-notifications.md). Keep stdout as provider-valid JSON and log a bounded, sanitized failure reason.

The original report is a Gemini Windows SessionEnd hang near `reader.join(...)` after `git rev-parse`; `hooks/families/scan_secrets.py:180-264` already has deadlines but uses a daemon thread blocked in `process.stdout.read`. Its main thread can still block while closing a pipe on Windows. Python's `subprocess.run(capture_output=True)` uses pipe reader threads on Windows and, after timeout, calls `communicate()` again, so the idea's literal replacement does not establish a fix. See [Python subprocess documentation](https://docs.python.org/3/library/subprocess.html) and [CPython's implementation](https://github.com/python/cpython/blob/main/Lib/subprocess.py). Existing POSIX stalled-Git tests in `scripts/test-hooks-secrets-scanner.sh` and `scripts/test-gemini-hooks-secrets-scanner.sh` do not exercise native Windows pipe behavior.

### ExecPlan acceptance

- Add a public hook-input regression that launches a stalled Git shim, plus a second shim that exits while a child retains stdout open. Use an outer watchdog so a regression cannot stall the test suite. Require bounded completion, no reader-thread join, no leaked temporary file, no secret-bearing output, valid provider JSON, block-mode denial, and session-end incomplete-scan warning.
- Run those cases through generated Copilot and Gemini hooks on POSIX and native Windows, including a Windows `git.cmd` shim. Also test successful Git output, expected no-HEAD nonzero, unexpected nonzero, partial stdout before a hang, oversized output, output-file failure, and whole-scan deadline. The scanner must never report clean from incomplete output.
- Cover Codex through the user-level scan-secrets adapter and registration introduced by [Security Hook Notifications](security-hook-notifications.md). Verify identical scanner decisions through its provider envelope. Distinguish source tests, installed-hook checks, and a documented live Windows SessionEnd check; automated Windows tests plus checklist satisfy the map's acceptance gate.
