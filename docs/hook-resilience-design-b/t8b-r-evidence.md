# T8b-R scanner registration evidence

T8b-R repairs only the registration assertions in the three maintained scanner shell suites. The accepted T8b product policy remains the source of expected registrations. The private task branch is `codex/design-b-t8b-r`, initially based on `419d20d5a38f4ca0284ab126ddfdbcae0aedaf79` (tree `e7feafc3ef9188db5aeecb00459a4bd7e28611dd`). This evidence file and the three suites are the complete task ownership boundary. The required local Python 3.14 and actual hosted Python 3.13 scanner proofs now pass; primary retains independent review and integration ownership.

## Actual hosted red

Primary supplied the actual macOS failure from [run 38980469324](https://github.com/japurcell/skills/actions/runs/38980469324), exact published snapshot `0c2282f4c0f42681c229aa4bcad6a09026707f90`. Preflight, recovery, and security reporting passed. The Codex scanner step failed immediately at inline Python assertion line 9 because the existing test required automatic `scan-secrets.py` placement in `PreToolUse` and `Stop`. Source inspection found the same obsolete expectation in the existing Copilot and Gemini registration checks. This repair does not reinterpret that red as a scanner detection failure.

## Current positive assertions

Codex checks one Guardian `PreToolUse` handler with its tool matcher and one historical-status `Stop` handler, including command type, Windows command variant, timeout, and visible status field. Copilot checks Guardian and observability on `preToolUse`, status and observability on `agentStop`, and the preserved bell and observability on `sessionEnd`, including Bash/PowerShell variants, event attribution, configured modes/timeouts, and relative ordering. Gemini checks Guardian, observability, and RTK on `BeforeTool`, historical status and observability on `AfterAgent`, and preserved `SessionEnd` observability. Its status registration retains the logical `scan-secrets` name so installed disabled-hook intent can survive migration.

A source-only comparison against the task base confirms that the Codex direct scanner/capture tail is byte-identical, and both other suites retain byte-identical direct scanner test bodies and main calls except the two renamed registration checks. No findings, clean, warn/block, malformed-input, audit, timeout, redaction, mode, or native capture assertion was removed, skipped, or weakened. No product, generated registration, workflow, registry, shared plan, installer, or KB file changed.

## Static validation

`rtk proxy bash -n` passed for all three owned scripts. Parser-only `compile` checks passed for all five updated inline Python registration blocks. `rtk git diff --check` passed. These checks executed no hooks, scanners, capture suites, generators, installers, or benchmarks.

## Composed local proof

The provisional private checkpoint rebased without conflict onto accepted T1-CI at `211d7c83f818aaf3790f87d82de18dca231ced5a`. The tested candidate is `bff403f5e0277dd1d172b5b0e14046e17abcb1c5`, tree `4801d0b94951a4a4d614c40556ceeb7b9e8548ca`. Every scanner test byte survived the rebase unchanged. A 3,451-file tracked SHA-256/mode manifest was frozen before execution and verified unchanged after all three suites. It is retained at `/private/tmp/design-b-t8b-r-proof/composed-source-manifest.json`, SHA-256 `0568d2a64b86c591b9a08cdfabcfb071c7e6d0b4dae2896362062ba95a37905b`.

The actual runtime was native macOS 26.7.1 arm64, Python 3.14.6, Bash 3.2.57, Apple Git 2.54.0, jq 1.7.1-apple, and RTK 0.51.0. The complete suites ran serially from `/Users/adam/.codex/worktrees/design-b-t8b-r/skills`. Each suite used a fresh disposable HOME, USERPROFILE, CODEX_HOME, XDG roots, TMPDIR, audit, and observability paths; `OBSERVABILITY_TESTING=1`, `GIT_CONFIG_GLOBAL=/dev/null`, `GIT_CONFIG_NOSYSTEM=1`, and `GIT_TERMINAL_PROMPT=0` prevented real-home state and interactive Git behavior. Exact environments and resolved tools are in each receipt.

The wrapper commands were `rtk proxy /Users/adam/.pyenv/versions/3.14.6/bin/python3 /private/tmp/design-b-t8b-r-proof/run-one.py PROVIDER`, with `PROVIDER` equal to codex, then copilot, then gemini. The wrapper executed these exact maintained commands, without a separate capture invocation:

```sh
rtk proxy bash scripts/test-codex-hooks-secrets-scanner.sh
rtk proxy bash scripts/test-hooks-secrets-scanner.sh
rtk proxy bash scripts/test-gemini-hooks-secrets-scanner.sh
```

| Provider | UTC interval on 2026-10-16 | Seconds | Exit | Scanner log SHA-256 |
| --- | --- | ---: | ---: | --- |
| Codex | 23:39:58.833284 to 23:41:04.926745 | 66.093 | 0 | `87f2fd28d7145eb1786943ac9aff78a10421318cfb0a2e3e5d3072469d31d9df` |
| Copilot | 23:41:10.205156 to 23:42:37.865790 | 87.659 | 0 | `8476c2d7b121cd6bd7ab7e1221ae944416aada8b20df914ebc9f8e1fc653f23c` |
| Gemini | 23:42:41.654929 to 23:44:00.968654 | 79.313 | 0 | `8903d0adb8b918b1138187f8497ca712df62cdb1fa550748c26d77cfff848986` |

Logs and receipts are `/private/tmp/design-b-t8b-r-proof/PROVIDER/scanner.log` and `receipt.json`. Receipt SHA-256 values are Codex `7b03143026cfbd1b1a656fb20e5eb598fa38a6b6d6e96fb12a1b70742b45f080`, Copilot `89873c09450c3f2cc8d1f149157ad4e83df4aae9359da18213a052713b4428f6`, and Gemini `f0a2859f938a25d7c37bf1731641ad3ecad33945577bed89c7efbb674b21a293`.

Each provider log contains all four unique block/warn and clean/findings native Darwin evidence cases. All 12 rows report actual `EAGAIN` (35), restored original soft process limits, and retained post-lowering hard limits. The existing capture assertions check the numeric before/lowered/after limits before emitting a row. Darwin clamped the child hard limit in these observations; this does not claim that an unprivileged child restored the prior higher hard limit. The wrapper parent retained `[10666, 16000]` before and after every suite. The saved-log verifier checks duplicate fields, exact event schemas, all required unique cases, receipt/log hashes, and unchanged input bytes/modes. Its 12 retained rows and verification receipt are `/private/tmp/design-b-t8b-r-proof/verification.json`, SHA-256 `4d4aef94f7e9b93e19104566ffafcd87f7205598e4d3e6e6cd4f5641f470edaa`.

| Test source | POSIX mode | SHA-256 |
| --- | --- | --- |
| `scripts/test-codex-hooks-secrets-scanner.sh` | 755 | `c2ffb3fabfb61b2b628c2a3ba18c047432cdff2c8898855899c8b603f9306a17` |
| `scripts/test-hooks-secrets-scanner.sh` | 755 | `68bfb47b2b4884e799cd3b1d1bac8117fb3f355796b46719adcae9a9f4456e5f` |
| `scripts/test-gemini-hooks-secrets-scanner.sh` | 755 | `2715b4d95d3dbb1174002ab4b381446caf17080e490a4a47373153f74eb438c8` |
| Unchanged `scripts/test-scan-secrets-capture.py` | 755 | `fdf9314ea62508d405871a2870dda8c7da46b2ecca435378e11aaf2a7026d7d3` |

One initial disposable wrapper launch failed before executing any suite because its minimal PATH omitted RTK at `/Users/adam/homebrew/bin/rtk`. The prelaunch receipt is retained in `/private/tmp/design-b-t8b-r-proof/codex-prelaunch-failed/receipt.json`; it records `suite_executed=false`. Correcting only the disposable wrapper PATH allowed the complete three-suite run above. No source assertion or test control changed in response. All local groups finished, and the functional window was released to primary at 23:44 UTC.

## Actual hosted Python 3.13 proof

The complete [macOS run 38986235261, job 117258250262](https://github.com/japurcell/skills/actions/runs/38986235261/job/117258250262) passed all three maintained scanner suites and the exact 12-case native Darwin validator. Primary published snapshot `ee6d5541ed73cd9a9927dd86c257b2d7288d7289` from candidate `8b5f974d6528788477f5d78d79180a3bc9af5d4c`. Independent Git inspection confirms that both names resolve to tree `2e76bf7b3b8e32efa59ea4da8b04e9c311f941df`.

The actual hosted runtime was macOS 26.6.2 arm64, Python 3.13.16, Bash 5.3.20, Git 2.56.0, jq 1.8.2, and RTK 0.51.0. The full log records each complete maintained shell command, each provider capture PASS line, all 12 unique native rows, the validator message `Verified all 12 native Darwin capture cases with restored soft process limits.`, and job completion. The hosted commands are the same three maintained shell commands listed above, with `2>&1 | tee "$RUNNER_TEMP/hook security/logs/PROVIDER-scanner.log"` under Bash `-e -o pipefail`. Each suite ran its own transitive capture checks; no extra capture run was added. The logged disposable HOME, USERPROFILE, CODEX_HOME, XDG, TMPDIR, audit, and observability settings preserve the same isolation contract.

| Provider | First and last logged step timestamps, UTC 2026-10-17 | Native cases | Result |
| --- | --- | ---: | --- |
| Codex | 00:31:11.9462680 to 00:32:23.9086310 | 4 | pass |
| Copilot | 00:32:23.9477740 to 00:34:00.1183610 | 4 | pass |
| Gemini | 00:34:04.9531940 to 00:35:43.7020690 | 4 | pass |

Saved full log `/private/tmp/design-b-macos-composed-38986235261-full.log` has SHA-256 `5e256d0a487e372194b61d53bc34c228f42e5f68152d42d53b1ee7bfa2315999`; scoped proof `/private/tmp/design-b-macos-composed-38986235261-proof.log` has SHA-256 `5d4344e7ed5b49e668c0407cf8de96b0ebe8b2930fe6baf98fc219d3706fbc40`. Both hashes were independently verified. The transport receipt `/private/tmp/design-b-macos-composed-38986235261-receipt.json` has SHA-256 `baa3221ad0b70ac05815aafb1e778ae14b70216ec3eb1148f0d175845a0acd72`. The scoped saved-log verifier retains every native row, actual runtime, and required completion observations in `/private/tmp/design-b-t8b-r-proof/hosted-38986235261-verification.json`, SHA-256 `412a067932610040efe2e3f7a1c02f0c06260955b6be09810b52cbf6b262f7a0`.

## Input preservation and remaining boundaries

The three hosted shell blobs and SHA-256/modes exactly match the local passing source table above. A conservative 130-file dependency closure also matches the hosted tree byte-for-byte and mode-for-mode. It covers all canonical `hooks/` files, all provider-local assets under `.codex/hooks/`, `.copilot/hooks/`, and `.gemini/hooks/`, the Codex/Gemini configuration templates, all three maintained shells, the capture suite, and every transitive shell/Python test helper, including `hook_test_support.py`. The Copilot configuration is included under `.copilot/hooks/`. The frozen closure manifest is `/private/tmp/design-b-t8b-r-proof/scanner-hosted-input-closure.json`, SHA-256 `3eb4210344c1717ed502bf26d3cb53477ffd2305d8025c93901498a9403e29f4`. Static verifier `/private/tmp/design-b-t8b-r-proof/verify-hosted-closure.py` checks the complete tracked input set, hosted blob bytes, and actual modes against that manifest; keeping it exact is the final rebase preservation gate.

This reconciliation rebases only the private R8 branch onto accepted base `327f7732`. The hosted tree includes separate provisional preflight source in `scripts/verify-security-fixture-patch.py` and its test; those files are neither imported nor sourced by these scanner suites or their helper closure. They are not imported into the accepted base by this task. The hosted 29-method preflight suite also passed in 187.354 seconds, but its earlier `incomplete_scan` cause remains separate and open under T1. No T1 repair acceptance is claimed here.

The bounded registration repair now has its required local Python 3.14 and actual hosted Python 3.13 proof. Primary still owns review, integration, archival, and the overall milestone state. No new functional execution was used for this evidence reconciliation or source comparison. Native Windows, authenticated provider delivery, and broader preflight acceptance remain separate. No live-home installation, trust change, automatic checkpoint, external task-branch push, or KB pass occurred in this task.

## Earlier preflight-blocked hosted attempt

The earlier clean hosted candidate was `be25fd71b26d74d1d30493516834c3a81368089a`, tree `8bef11c3c9313d38c73369ecd13dd28823d47b03`, composed onto accepted base `7f9da9ebbd3d52ca6f3b3455b784b1e9763fd59b`. Compared with the earlier local-tested tree, existing changed paths are only this evidence, shared ExecPlan/delegation documents, and accepted W0 Windows-only installer files `scripts/scan_install_windows.py` and `scripts/test-install.ps1`. All scanner/runtime/capture/helper/test inputs remain byte/mode identical, so no local rerun was warranted. The 3,452-row candidate manifest is `/private/tmp/design-b-t8b-r-proof/host-candidate-source-manifest.json`, SHA-256 `01ebda18fb9bd710059f305f758e673a2c604f62a8c8bb221bc0d3781de82fb6`. Primary independently verified that candidate manifest, all three local receipts/logs, and all 12 native Darwin cases; its receipt is `/private/tmp/design-b-t8b-r-proof/primary-review-receipt.json`, SHA-256 `c39e38e4b774bbffc2eea4e7bf8af75d2b00d3e9d2d286c4d51079ed6023bbb6`.

Primary verified full-tree equivalence and published snapshot `4b52fec3f43c65801cceb6c999fd489f9019d032` for actual [macOS run 38983363556](https://github.com/japurcell/skills/actions/runs/38983363556). The run failed before reaching the scanner suites: the renewed 28-method preflight suite ran for 281.088 seconds with two failures and two errors. Primary reported an ordinary process-observer measurement of 0.621 seconds exceeding 0.5 seconds, child 15/20-second watchdog failures, and an active-timeout measurement of 16.883 seconds exceeding 16 seconds. This run supplies neither a hosted scanner pass nor a red against the scanner registration repair. No scanner-suite or native-validator result from that run is claimed. The separate unrepaired main-tree [run 38982851210](https://github.com/japurcell/skills/actions/runs/38982851210) reproduced the obsolete Codex inline line-9 registration assertion and does not contain this repair; the original hosted red remains run 38980469324 above.
