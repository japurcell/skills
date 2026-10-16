# T8b-R scanner registration evidence

T8b-R repairs only the registration assertions in the three maintained scanner shell suites. The accepted T8b product policy remains the source of expected registrations. The private task branch is `codex/design-b-t8b-r`, based on `419d20d5a38f4ca0284ab126ddfdbcae0aedaf79` (tree `e7feafc3ef9188db5aeecb00459a4bd7e28611dd`). This evidence file and the three suites are the complete task ownership boundary.

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

## Hosted acceptance and limits

Actual hosted Python 3.13 verification remains pending. Primary owns exact candidate publication and return of hosted logs; accepted T1-CI is already composed into the local tested candidate. Local proof does not establish native Windows or authenticated provider delivery. No live-home installation, trust change, automatic checkpoint, external task-branch push, or KB pass occurred in this task.
