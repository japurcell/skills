# Security validation

- Exercise public provider envelopes for allow, denial, retry, incomplete capture, safe counts, and bounded error handling.
- Incomplete scanner results must remain distinguishable from clean scans.
- Isolate fake-secret fixtures and test homes. Do not put real credentials into fixtures, output, logs, or version control.
- Verify bounded Git capture and descendant cleanup; native Windows behavior requires native execution.
- Preserve failed warm/cold benchmark observations and compare equivalent workloads before claiming improved performance.
- Use the current scanner and guardian suites as the detailed behavioral contract rather than copying thresholds into many notes.
- Guardian public-envelope changes retain the focused Codex suite alongside Copilot/Gemini and the shared [security-banner suite](../../scripts/test-security-banners.py) in [the suite registry](../../scripts/test-all.py). Suite coverage does not imply global handler registration.
- For scanner/capture/banner changes run affected public [Codex](../../scripts/test-codex-hooks-secrets-scanner.sh), [Copilot](../../scripts/test-hooks-secrets-scanner.sh), [Gemini](../../scripts/test-gemini-hooks-secrets-scanner.sh), [capture](../../scripts/test-scan-secrets-capture.py), and [banner](../../scripts/test-security-banners.py) suites. Index/merge changes require [merge tests](../../scripts/test-scan-secrets-merge.py) through all three providers.

## Acceptance evidence

- Before release or performance acceptance, read [the release verifier](../../scripts/verify-hook-release.py) and the affected public suites. A successful benchmark exit proves decision correctness, not performance acceptance. Inventory every high-rate registration, including streamed chunks, before choosing cases.
- For frozen-source sequential timing, disposable benchmark isolation, and subprocess-versus-provider timing limits, follow [timing probes](scripts-and-installers.md#timing-probes). Compare complete subprocesses under equivalent provider, interpreter, input, and logging conditions; retain source fingerprints, raw samples, first-process/warm/cold results, variation, concurrency, and provider evidence separately. Use [performance optimization](../../skills/default/addy-performance-optimization/SKILL.md#step-4-verify-keep-or-revert) for cache, contention, and timeout-headroom qualifications.
- Preserve regressions and inconclusive ablations; optional optimizations do not justify blanket gains. The shared reader bounds raw bytes, structural markers, depth and completion time before decoding; Guardian traversal/content/executable limits apply after decoding. Preserve true units and the first failing budget. Avoid universal raw-JSON memory-bound claims.
- The original inline-matcher variants in [the optional ablation CLI](../../scripts/benchmark-tool-guard-optimizations.py) require a frozen checkout of `84eae394` as `--root`; current extracted entrypoints cannot prepare them. Trusted `common-before` and matcher references are `5f1aa7e` and `9bcc6ff5`. Use a disposable `--evidence` directory; these legacy comparisons do not replace current acceptance evidence.
- Credential controls require actual findings; unsafe/unreadable captures require incomplete results. Generic denial does not prove credential detection. Force-push controls must target the configured protected branch (such as `main`); `HEAD` alone does not exercise that rule.
- A timed-out/incomplete review yields partial findings, never security approval. Apply the [review completeness rule](../../skills/default/addy-code-review-and-quality/SKILL.md#review-completeness) before reporting a verdict.
- For an authorized capacity change, prove supported workload completion, oversize incomplete behavior, late fake-credential and conflict-index-only detection, binary/text coverage, chunk boundaries, worktree/untracked cases, and documented concurrent-edit limits through current explicit check/gate and historical-status envelopes. Regenerate canonical output; separate source, installation/trust, and native delivery proof. Historical incidents authorize no budget increase or new knob.

## Native Windows capture

- Read [the native PowerShell acceptance suite](../../scripts/test-scan-secrets-windows.ps1) before changing capture. Preserve all three provider JSON envelopes across failures, descendants, size bounds, malformed output, temporary-file handling, and unborn-versus-failed HEAD detection. Assert temporary-file cleanup immediately after return; retain actionable provider/mode/scenario/filename diagnostics and six total Gemini stress executions per selected case (base case plus five repeats).

Evidence: `scripts/test-scan-secrets-*.py`, `scripts/test-tool-guard-*.py`, [bounded JSON reader](../../hooks/families/common.py), and [hook-testing](hook-testing.md), checked 2026-10-21. Recheck after policy or capture changes.
