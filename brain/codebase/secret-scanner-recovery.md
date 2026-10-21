# Secret scanner incident recovery

## Evidence before repair

- Preserve the active merge, legitimate retained evidence, unrelated handlers, existing configuration, and owner trust decisions. Record the source revision, deployed version/build, exact registration, platform, safe failure phase/counts/limits, and installed hashes before repair. Matching build text alone does not authenticate installed bytes.
- Compare source and installed implementations; current clean Git status cannot certify earlier pending snapshots. The historical 8,403,665-byte observation was the first rejected reservation, not a complete inventory. `audit_outcome=written` reported an audit write, not successful scanning or independently collected audit evidence.
- If an active gate prevents agent diagnostics, use an ordinary human terminal outside the chat with the trusted absolute interpreter and reviewed installed diagnostics path. Keep the guard enabled during bounded maintenance patches; diagnostics does not authorize ordinary helpers through a blocked gate.
- Use the [current standalone diagnostics contract](../../README.md#hook-diagnostics). It collects bounded metadata without scanning, granting exemptions, authenticating execution, or proving clean content. Report only sanitized counts, actual limits, and failure phase with verified remediation; invent no configuration knob.

## Reproduction and acceptance

- Reproduce in disposable repository/merge, home, and audit/log paths using [scanner fixture support](../../scripts/scanner_test_support.py) and [recovery fixtures](../../scripts/test-hook-diagnostic-recovery.py). Remove inherited skip/allowlist settings and measure the actual inventory rather than manufacturing a historical count.
- Exercise the applicable current explicit check/gate CLI and provider historical-status envelope. Historical automatic PreToolUse/Stop scanning and repeated Stop recovery loops are superseded. Status stays incomplete when inspection was incomplete and remains nonblocking; see [End Turn boundary](security-hooks.md#end-turn-boundary).
- For a future authorized repair, preserve distinct conflict versions and pair accepted larger workloads with late fake credentials and conflict-only credential controls. Keep over-limit, capture-failure, and incomplete cases; follow [security acceptance](security-testing.md#acceptance-evidence). Regenerate from canonical sources and prove installation/trust and native delivery separately.
- For authorized capacity repair, do not use permanent warnings, skips, allowlists, or evidence exclusions as a substitute for complete supported inspection. Preserve the current explicit-check architecture; this rule does not restore automatic global scanning.
- Do not hand-edit installed scanner constants to raise capacity. Change canonical source, regenerate providers, and verify authorized deployment separately to avoid source/installation drift.

## Legacy diagnostics compatibility only

- `hooks-diagnostics-v1` belongs only to old scanner registrations. The strict native Codex request was `{"cmd":"hooks-diagnostics-v1","login":false}` with no wrappers, extra arguments, or working directory. It returned deny-only bounded diagnostics and `not_scanned`; the marker was never executed. Use [the recovery suite](../../scripts/test-hook-diagnostic-recovery.py) for exact matching rules rather than treating this as a current bypass or a live dispatch guarantee.

Evidence: [current scan/gate architecture](../../README.md#explicit-secret-checks-and-git-gates), [merge controls](../../scripts/test-scan-secrets-merge.py), and [capture contract](../../hooks/runtime/scan_git.py), reviewed 2026-10-21. Historical incidents identify causal limits and evidence gaps, not a current defect or an approved capacity target.
