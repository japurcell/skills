# Security validation

- Exercise public provider envelopes for allow, denial, retry, incomplete capture, safe counts, and bounded error handling.
- Incomplete scanner results must remain distinguishable from clean scans.
- Isolate fake-secret fixtures and test homes. Do not put real credentials into fixtures, output, logs, or version control.
- Verify bounded Git capture and descendant cleanup; native Windows behavior requires native execution.
- Preserve failed warm/cold benchmark observations and compare equivalent workloads before claiming improved performance.
- Use the current scanner and guardian suites as the detailed behavioral contract rather than copying thresholds into many notes.

Evidence: `scripts/test-scan-secrets-*.py`, `scripts/test-tool-guard-*.py`, and [[hook-testing]], checked 2026-10-20. Recheck after policy or capture changes.
