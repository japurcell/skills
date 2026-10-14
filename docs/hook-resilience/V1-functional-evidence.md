# V1 functional verification and installed-assets proof

This is composed functional evidence, not a claim that a new all-51 aggregate passed. The original frozen aggregate remains **46 successful processes / 5 failed in 879.5s**, including **three explicit Windows platform skips**. Complete original logs and all failures remain in [Phase 1 evidence](V1-phase1-evidence.md). The five failures now map to **two corrected-environment repeats, two T8 reporting-contract repairs, and one T9 fixture-isolation repair**. No test was removed, skipped to obtain green, or weakened.

The actual V1 installation ran on `0ecd490d07c34519e86f10719ef778cebff73fae`. The coordinator's approved source target is `3288cf4e8fe8899b9f179c49e6290e99f490051f`; its only changes relative to that product checkout are documentation and T9's shared fixture support. Both independent reviewers accepted the integrated repairs. The coordinator repeated both full observability suites after rebase with all three completion markers. The V1 branch rebased cleanly to this exact target, confirmed expected file changes and identical runtime fingerprints, and froze at `6c1623ff06d58566cf659658c9a92196b71bff7d`. [Release evidence](V1-release-evidence.md) records the finite-resource pass and rejected latency acceptance.

## Actual disposable installation

The verifier invoked the real `bash scripts/install.sh` as a child of `rtk proxy python3 /private/tmp/hook-v1-installed-probe.py`. The home path contains spaces and an apostrophe. HOME, CODEX_HOME and XDG homes were disposable, `OBSERVABILITY_TESTING=1` and a writable disposable generic observability path were set, and inherited audit/provider-specific overrides were cleared. No live home or authenticated provider was used.

The first install exited zero in **2.362s**. All **36 installer-owned provider Python/shell scripts and helpers** matched source SHA-256 and mode **0755**. The inventory follows all tracked Copilot/Gemini runtime scripts plus the explicit Codex installer-owned list, excluding Codex project-only helpers that are not installed globally. Seeded custom handlers/settings survived for all three providers. Installed doctor responses were nonmutating, bounded (1,958/2,145/2,073 bytes), `not_scanned`/`not_attempted`, with complete asset sets and zero missing/duplicate owned registrations. Owned counts were Codex 4/Copilot 19/Gemini 16; intentional custom unowned counts were 2/1/1, so doctor correctly retained uncertain registration health rather than claiming all handlers were owned.

The second actual install exited zero with **no changed regular-file bytes or modes** throughout the disposable home. Before/after file-and-mode inventory fingerprint was `4169ed6cc3112da2195cdbd2b05af8dee56ba0ae8cdef84b829f33190388b06c`. This is a regular-file fingerprint, not native Windows ACL or symlink identity proof. The maintained installers separately retain their link/refusal/ownership tests.

Asset hashes, config hashes, exact doctor reports, preservation assertions, repeat-install fingerprints and raw installer output are in [installed proof](V1-installed-assets.json), [first installer log](V1-installer-first.log.gz), and [second installer log](V1-installer-second.log.gz). T7's actual Bash/macOS PowerShell registered-command tests additionally prove hostile PYTHONPATH/site startup and later PATH replacement do not run, ordinary allow/deny/audit behavior survives, appended operands remain unowned, and repeated registrations remain unchanged; see [T7 integration](T7-integration-evidence.md) and [T7 evidence](T7-evidence.md).

## Evidence reuse and source identity

Read-only generated freshness passed all 38 outputs before and after the new actual-install proof. The checkout was clean. [Source comparisons](V1-source-reuse.json) record five empty diff groups against their exact evidence revisions: original common/scanner/stream/observability/registry; T6 Guardian policy/helpers and public tests; T7 combined runtime/installers/recovery; T8 merge/portable PowerShell; and unchanged runner mechanics/helpers. The relevant source and interaction proof supports reuse. A documentation-only rebase does not justify rerunning unchanged passing suites.

[Runtime fingerprints](V1-runtime-fingerprints.json) retain 74 canonical/generated/installer/config source assets, modes and hashes. The inventory SHA-256 is `76e5086f4a3bc110e3d29547df04fabf5c64f6c3a469962dffd60e26267087b3`. [Phase 2 provenance](V1-phase2-freeze.json) confirms these bytes after T9 integration and preserves the measured candidate commit separately.

T6's whole-label repair public checks passed reporting 11, banners 14, native 26, shell 17, limits 18, corpus 153 and all three provider Guardian suites. The combined T6/T7 merger then passed reporting 11/recovery 12/diagnostics 8/Codex merge/generator 26/freshness 38. T8 passed full merge 33 in 202.541s; combined-tree delimiter and portable PowerShell repeats also passed. T9 preserved the original untraced failure limit, proved an unwanted maintenance launch and a concrete controlled SQLite lock seam, seeded only unrelated fixture sentinels, and retained intentional maintenance/locking/cleanup assertions. Both full provider suites and repeated affected fixtures passed; primary repeated both full suites after rebase. Their reports remain the proof, rather than conflict-free rebasing alone.

## All51 registered suite provenance

`pass_reused` means an original passing result with verified unchanged source/covered interactions. Other statuses identify the current repaired or corrected result and are expanded with exact evidence references in [the machine-readable map](V1-functional-map.json). Three `platform_unverified` rows remain explicit skips. The macOS PowerShell installer passed with junction creation unavailable; portable PowerShell envelope coverage is not native Windows acceptance.

| # | Registered command | Original | Current evidence status |
| --- | --- | --- | --- |
| 1 | `bash scripts/test-addy-install.sh` | PASS | `pass_reused` |
| 2 | `bash scripts/test-cleanup-skill-workspaces.sh` | PASS | `pass_reused` |
| 3 | `bash scripts/test-codex-hooks-startup.sh` | PASS | `pass_reused` |
| 4 | `bash scripts/test-codex-repository-okf.sh` | PASS | `pass_reused` |
| 5 | `bash scripts/test-codex-hooks-secrets-scanner.sh` | PASS | `pass_reused` |
| 6 | `bash scripts/test-gemini-hooks-auto-ingest.sh` | PASS | `pass_reused` |
| 7 | `bash scripts/test-gemini-hooks-observability.sh` | FAIL | `pass_T9_integrated` |
| 8 | `bash scripts/test-gemini-hooks-okf-lint.sh` | FAIL | `pass_environment_corrected` |
| 9 | `bash scripts/test-gemini-hooks-rtk.sh` | PASS | `pass_reused` |
| 10 | `bash scripts/test-gemini-hooks-secrets-scanner.sh` | PASS | `pass_reused` |
| 11 | `bash scripts/test-gemini-hooks-startup.sh` | PASS | `pass_reused` |
| 12 | `bash scripts/test-gemini-hooks-tool-guard.sh` | PASS | `pass_T6_repair_reused` |
| 13 | `bash scripts/test-hooks-auto-ingest.sh` | PASS | `pass_reused` |
| 14 | `bash scripts/test-hooks-observability.sh` | PASS | `pass_T9_integrated` |
| 15 | `bash scripts/test-hooks-okf-lint.sh` | PASS | `pass_reused` |
| 16 | `bash scripts/test-hooks-rtk.sh` | PASS | `pass_reused` |
| 17 | `bash scripts/test-hooks-secrets-scanner.sh` | PASS | `pass_reused` |
| 18 | `bash scripts/test-hooks-startup.sh` | PASS | `pass_reused` |
| 19 | `bash scripts/test-hooks-tool-guard.sh` | PASS | `pass_T6_repair_reused` |
| 20 | `bash scripts/test-codex-hooks-tool-guard.sh` | PASS | `pass_T6_repair_reused` |
| 21 | `python3 scripts/test-codex-agents.py` | PASS | `pass_reused` |
| 22 | `python3 scripts/test-install-codex-hooks.py` | PASS | `pass_T7_combined` |
| 23 | `python3 scripts/test-probe-provider-hook-delivery.py` | PASS | `pass_reused` |
| 24 | `python3 scripts/test-generate-hooks.py` | PASS | `pass_T7_combined` |
| 25 | `python3 scripts/test-rtk-stable.py` | PASS | `pass_T7_reused` |
| 26 | `python3 scripts/test-security-banners.py` | PASS | `pass_T6_repair_reused` |
| 27 | `python3 scripts/test-security-reporting.py` | PASS | `pass_T7_combined` |
| 28 | `python3 scripts/test-hook-input-bounds.py` | PASS | `pass_reused` |
| 29 | `python3 scripts/test-hook-diagnostics.py` | PASS | `pass_T7_combined` |
| 30 | `python3 scripts/test-hook-diagnostic-recovery.py` | PASS | `pass_T7_combined` |
| 31 | `python3 scripts/test-scan-secrets-merge.py` | FAIL | `pass_T8_repair` |
| 32 | `python3 scripts/test-scan-secrets-stream-component.py` | PASS | `pass_reused` |
| 33 | `python3 scripts/test-scan-secrets-streaming.py` | PASS | `pass_reused` |
| 34 | `python3 scripts/test-tool-guard-false-positives.py` | PASS | `pass_T6_repair_reused` |
| 35 | `python3 scripts/test-tool-guard-native-data.py` | PASS | `pass_T6_repair_reused` |
| 36 | `python3 scripts/test-tool-guard-shell-data.py` | PASS | `pass_T6_repair_reused` |
| 37 | `python3 scripts/test-tool-guard-limits.py` | PASS | `pass_T6_repair_reused` |
| 38 | `python3 scripts/test-benchmark-high-rate-hooks.py` | PASS | `pass_reused` |
| 39 | `python3 scripts/test-verify-hook-release.py` | PASS | `pass_reused` |
| 40 | `pwsh -NoProfile -File scripts/test-install.ps1` | PASS | `pass_T7_reused` |
| 41 | `pwsh -NoProfile -File scripts/test-codex-hooks-windows.ps1` | FAIL | `pass_T8_repair_portable_only` |
| 42 | `pwsh -NoProfile -File scripts/test-scan-secrets-windows.ps1` | SKIP | `platform_unverified` |
| 43 | `pwsh -NoProfile -File scripts/test-repository-okf-windows.ps1` | SKIP | `platform_unverified` |
| 44 | `pwsh -NoProfile -File scripts/test-lifecycle-messages-windows.ps1` | SKIP | `platform_unverified` |
| 45 | `bash scripts/test-install.sh` | PASS | `pass_T7_reused` |
| 46 | `bash scripts/test-okf-lint.sh` | PASS | `pass_reused` |
| 47 | `bash scripts/test-repo-root.sh` | PASS | `pass_reused` |
| 48 | `python3 scripts/test_helpers.py` | FAIL | `pass_environment_corrected` |
| 49 | `python3 skills/spec-to-tasks/evals/test_grade_benchmark.py` | PASS | `pass_reused` |
| 50 | `python3 skills/prd-ralph-loop/evals/test_grade_benchmark.py` | PASS | `pass_reused` |
| 51 | `python3 scripts/test_test_all.py` | PASS | `pass_reused` |

## Limits and next gate

No native Windows/ACL/junction or authenticated provider dispatch is established. No V1 release latency or finite-resource acceptance is claimed by this functional document. The coordinator explicitly authorized Phase 2 only after all reviews/probes/tests/generation ended and the clean rebase/fingerprint checks pass. V1 must retain full 108 resource and 156 timing case evidence per condition, prescribed raw samples/native decisions/completed logging, unchanged sources and gates; failures cannot be waived. The coordinator owns final plan reconciliation and the single KB pass.
