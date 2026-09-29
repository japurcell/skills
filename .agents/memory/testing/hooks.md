---
type: Testing Guidance
description: Test routes for Codex, Copilot, and Gemini hook sources and installed copies
---

# Hooks - Testing

## Repo checks

- For a generated provider-hook or canonical `hooks/` change, run `python3 scripts/generate-hooks.py --check` before and after the relevant provider suites, plus `python3 scripts/test-generate-hooks.py`. Use `--write` only to refresh manifest-owned outputs; provider-local files with the generated header are not edit targets.
- Stable RTK setup and explicit commands: run `python3 scripts/test-rtk-stable.py`. Keep `bash scripts/test-hooks-rtk.sh` and `bash scripts/test-gemini-hooks-rtk.sh` for unchanged automatic forwarders. Native Windows config and real-command proof is `pwsh -NoProfile -File scripts/test-rtk-stable-windows.ps1` in the dedicated workflow; it must exit `0` rather than skip.
- Gemini RTK registration checks must assert that observability, security, and RTK handlers are present in the required relative order. Other maintained handlers may be inserted between them; fixed array indexes do not express this contract.
- After changing hook source, run `./scripts/install.sh` before any live validation because installed hooks execute from `~/.codex/hooks`, `~/.copilot/hooks`, or `~/.gemini/hooks`, not from repo source paths.
- Centralize standard test environment helper utilities (such as `install_into_temp_home()`) in `scripts/test-common.sh` instead of duplicating them across individual test files.
- Read official hook docs before non-trivial changes and keep implementation aligned with them.
- The retained supported hook surface is Python-first; validate the Python entrypoints and installed copies rather than the retired shell format surface.
- Copilot hook checks:
  - `bash scripts/test-hooks-okf-lint.sh`
  - `bash scripts/test-hooks-auto-ingest.sh`
  - `bash scripts/test-hooks-startup.sh`
  - `bash scripts/test-hooks-observability.sh`
  - `bash scripts/test-hooks-secrets-scanner.sh`
  - `bash scripts/test-hooks-tool-guard.sh`
  - `bash scripts/test-hooks-rtk.sh`
- Gemini hook checks:
  - `bash scripts/test-gemini-hooks-okf-lint.sh`
  - `bash scripts/test-gemini-hooks-auto-ingest.sh`
  - `bash scripts/test-gemini-hooks-startup.sh`
  - `bash scripts/test-gemini-hooks-observability.sh`
  - `bash scripts/test-gemini-hooks-secrets-scanner.sh`
  - `bash scripts/test-gemini-hooks-tool-guard.sh`
  - `bash scripts/test-gemini-hooks-rtk.sh`
- Before treating Gemini `AfterAgent` as an enforced final-response boundary, run a live probe against the deployed CLI version and confirm the configured hook executes. Upstream issue `google-gemini/gemini-cli#27712` remains open for affected builds; simulated provider-envelope tests do not prove event delivery.
- Security banner contract: `python3 scripts/test-security-banners.py` checks Copilot, Gemini, and Codex Tool Guardian public envelopes, excerpt bounds, full quoted and JSON-field credential redaction, omission of unknown credentials in input context and matched Git remote URLs, exact banner/log excerpt parity, and safe fallback. Scanner suites check action-named block and warning messages. Native Windows workflow runs the Python banner suite; macOS execution does not establish native Windows acceptance.
- Codex hook checks:
  - `bash scripts/test-codex-hooks-startup.sh`
  - `bash scripts/test-codex-repository-okf.sh`
  - `bash scripts/test-install.sh`
  - `pwsh -NoProfile -File scripts/test-install.ps1` when PowerShell 7 is available
- Codex source remains inactive at `.codex/global-hooks.json`; fixture tests validate the user-global merge without writing to the real home directory. After a real install, review and trust the changed non-managed definition through `/hooks` before live validation.
- The Bash and PowerShell temporary-home installer suites assert installed Codex hook files and registrations against source. Stable RTK config proof runs separately so no user home is changed by tests.
- The Codex startup suite covers open-stdin completion and malformed-prefix time bounds, raw skill-file and final-context limits, large removable frontmatter, path containment, UTF-8 output, and POSIX audit-link defenses. Exercise PowerShell installer behavior and Windows audit reparse-point handling on a Windows host when available.
- `scripts/test-gemini-hooks-startup.sh` includes a negative missing-skill case that intentionally prints `Hook hard stop: Required skill file not found...`; trust the script exit status and assertions, not stderr alone.
- The multiple-skill case in `scripts/test-hooks-startup.sh` uses temporary caveman and universal-guidelines fixtures through `COPILOT_SKILLS_DIR`; it does not require the intentionally deleted writing-great-skills installation. Other startup cases still use the configured or installed caveman skill. Keep multi-file loading assertions independent of which optional skills are installed.
- **Dynamic-Cleanup traps:** When writing bash function-level traps under `set -u` (nounset), register local cleanup variables using single-quotes inside double-quotes (e.g. `trap 'rm -rf "'"$workdir"'"' RETURN`). This interpolates the variable at trap registration time, preventing unbound variable errors when the function exits and pops local scope before execution.

For source auto-ingest behavior, read [Hook Auto-Ingest Testing](hooks-auto-ingest.md). Skip it for unrelated hooks. For observability, trace, transcript, audit-log, or maintenance behavior, read [Hook Observability Testing](hooks-observability.md). Skip it for operational hooks.

## Live evidence

- `python scripts/test-probe-provider-hook-delivery.py` covers timestamped normal delivery and rejects completions with unmatched invocation IDs. For Gemini live latency, set `GOOGLE_CLOUD_PROJECT` in the same process as `gemini`, retain the nonce-visible transcript for verification, and report paired handler runtime separately from unmeasured provider startup-to-entry. A short handler runtime does not prove that a one-second hook deadline will be met.
- The Copilot CLI delivery probe uses a separate progress JSON line for each visible nonce before its final decision JSON. Invocation and completion markers without the visible nonce do not pass normal delivery. In CLI 1.0.88 a one-second hook timeout allowed a harmless Git read, recorded entry markers without completions, but displayed no timeout indication; keep that visible-timeout acceptance open instead of changing the verifier to accept silent timeouts.
- A force-push fixture must name a protected branch such as `main`, not `HEAD`, for the configured Tool Guardian pattern to match.
- Keep scanner audit paths, Tool Guardian logs, and PTY transcripts outside a disposable Git checkout during live hook checks. The scanner includes untracked files, so logs inside the checkout can become new findings and repeatedly block `Stop`. Remove only exact fake fixtures after recording results. On macOS, `/usr/bin/git` may fail through `xcrun` cache writes under Codex's read-only tool sandbox; use a verified native Git binary with `--no-optional-locks` when testing whether the hook permits safe Git reads.
- Copilot CLI: verify installed behavior from `~/.copilot/hooks/logs/observability.ndjson` or direct installed-script smoke tests.
- VS Code Copilot: inspect `GitHub Copilot Chat Hooks.log` and `GitHub Copilot Chat.log` for returned hook JSON and applied context.
- If VS Code omits `SubagentStart` for `runSubagent` child sessions, verify the direct `SubagentStart` hook is installed and use `SessionStart` as the fallback evidence.
- The Copilot secret-scanner suite verifies that malformed input, unexpected exceptions, and real block-mode findings emit runtime-specific deny decisions with exit `0`, while warn mode remains a JSON no-op.
- The Copilot and Gemini secret-scanner suites prepend stalling POSIX `git` and Windows `git.cmd` shims to `PATH`. They verify the public hook stdin/stdout path returns JSON within 8 seconds in warn mode and emits a deny decision in block mode.
- `scripts/test-scan-secrets-capture.py` is called by all three provider scanner suites. It uses an outer process-group watchdog at each generated JSON hook entry point for a Git descendant holding stdout, partial output before a stall, oversized and malformed output, unexpected nonzero, a committed repository whose HEAD verification fails, temporary-file failure, and a valid repository without HEAD. Incomplete cases require a denial or warning and an `incomplete` log status, never `clean`; the no-HEAD case must stay clean. `scripts/test-scan-secrets-windows.ps1` covers the same HEAD-failure distinction and other capture cases with a native Windows `git.cmd` shim and outer process timeout; a macOS `pwsh` skip is only syntax and registration evidence.
- `scripts/test-hooks-startup.sh` and `scripts/test-hooks-rtk.sh` must assert both `bash` and exact `powershell` command paths for Copilot hook registrations so Windows path regressions fail fast.
- The Copilot and Gemini RTK suites keep an initially empty POSIX pipe open to verify the first-byte 0.5-second bound, simulate the Windows `PeekNamedPipe` initial wait with a controlled clock, and require nonzero RTK stderr to stay out of bounded audit diagnostics.
- The Bash and PowerShell installer fixtures must prove generator freshness before destination mutation. A stale generated output exits `1` with the exact recovery command; controlled generator failure exits `2` without recovery advice. The PowerShell suite can skip its junction case on a host that cannot create junctions, which is not native-Windows proof.
- `scripts/test-hooks-startup.sh` now also verifies the repo-local `.github/hooks/hooks.json` startup, prompt-time, and final-response auto-ingest registrations while confirming `.copilot/hooks/hooks.json` no longer owns any auto-ingest wiring.
- The Copilot and Gemini OKF suites copy the adapters and valid two-bundle fixture into one checkout, exercise the public stdin/stdout seam, and cover central-diagnostic parity, provider envelopes, missing or invalid dependencies, timeout/`OKF900`, Windows rerun text, 20-item and serialized 8 KiB bounds, nested checkout paths, out-of-checkout decoy rejection, and simultaneous pending-ingest plus OKF failures. The Copilot suite keeps stdin open for complete, multiline, malformed, incomplete, and buffered-trailing payloads; requires bounded completion with child cleanup; and verifies UTF-8 output under simulated CP1252. Its registered stop-hook cases preserve source-ingest-first reasons even when both reasons require truncation.
- `bash scripts/test-codex-repository-okf.sh` covers project Stop registration, nested-directory command resolution, pass/finding/incomplete envelopes, bounded retry, 20-item output cap, checkout containment, audit deduplication, 4 KiB path cap, and audit-write failure. `pwsh -NoProfile -File scripts/test-repository-okf-windows.ps1` exercises native Windows provider envelopes and the registered Codex command; a macOS skip is not Windows proof.
- Registration assertions keep OKF out of user-global Copilot, Gemini, and Codex configs and out of post-tool events. Copilot registers one final-response coordinator for each stop event, while Gemini preserves source-ingest-first `AfterAgent` order and its millisecond timeout.
- `scripts/test-install.sh` verifies `.gemini/global-settings.json` is copied into `~/.gemini/settings.json` during install.
- Hook event compatibility contract lives in `.agents/instructions/hooks.md`.
