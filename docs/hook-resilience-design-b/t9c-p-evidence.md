# T9c-P macOS CI evidence

Status, 2026-10-16: CI wiring and local prerequisites are complete. The early hosted full run passed every step through status, then found one gate-test fixture portability error. The approved single-method repair passes its targeted red/green check. Final acceptance belongs to the primary's full integrated macOS Actions run and existing Windows workflow. No extra runners, diagnosis jobs, local full replay, registry changes or platform features are part of this task.

## Scope and source identity

Owned files are `.github/workflows/hooks-posix.yml`, the bounded existing method in `scripts/test-scan-secrets-git-gates.py`, and this evidence file. The primary owns the [active completion contract](ExecPlan.md), final composition, hosted transport, integration and coordinated knowledge pass. Target integration base is `4f2841c2`; no private T1 source is imported. The primary separately integrated simplified T1 at `1a1c3b8` for final composition. The early run used the older 28-method preflight and does not validate that newer source.

Initial wiring/prerequisite checkpoint is private `a749d3460a6fc53668ff6461470b040f1d2fc5f5`, starting at `fa58ef356923644b9850986e82cb85e9c3aea57e`. Detailed initial source/tool rows remain in that checkpoint and the retained receipts below. The initial accepted [source map](macos-ci-source-map.md) receipt SHA-256 was `9f065476966af59bcdecc19f354ea5f9d5cf59860be74b00dc05d0926fa90db0`; its superseded planning and local replay directions are historical. Accepted prerequisite identities supplied by the primary were T9b `f250a87c3a8f9ff5c665442e55512d7c6e80b2da`, I4 `cebf04eaefdce00af366d3140bce816b86cab6bf` and R8 `fd622fe9452cabb4155a39a423fc1eb090a4f6ba`.

Workflow SHA-256 remains `bbed38d1698ae9c14044ca0973c73b4c7d5d75970b1b265862a507b2ee18a4bc`. All eight original required test/freshness/validator steps remain exact. Native validator run-block SHA-256 is `3ca5e33ec2cbef943c7b3854d9cd4e955cbeb5041e1021ce97e37e045c2f2f18`. Thirteen additional full public commands appear once, followed by final generated freshness. The registry already contained all commands among 61 unique tuples, so neither registry nor assertions changed. Scanner shells already run capture; no duplicate aggregate capture is added. Explicit Bash pipefail and required native evidence remain intact.

## Prerequisites and static proof

The workflow provisions real Python 3.11 with `actions/setup-python@v7` and `update-environment: false`, exports absolute `TEST_UNSUPPORTED_PYTHON`, then selects Python 3.13. The [official v7 usage](https://github.com/actions/setup-python/blob/v7/docs/advanced-usage.md) documents those outputs and environment behavior. Exact Git LFS 3.8.0 is selected by Darwin architecture, checked against the [official release](https://github.com/git-lfs/git-lfs/releases/tag/v3.8.0) before extraction, exported as absolute `TEST_GIT_LFS` and placed first on PATH. Published ZIP hashes are amd64 `f1c17aeca0b4eaab9ea606226477dbed3b84b56fe0811a9f967d2ea2b2393c53` and arm64 `caff76a7d070d8160c89bc39b6e85d98f24135b6fed038a3b4de2590d25102d8`. Receipt `/tmp/design-b-ci-prerequisite-sources.json`, SHA-256 `ff0a92d9611731cbf2b98a927730924b50955e7ece71eced41b861b8d2c28624`, was independently compared with official assets; the assignment's arm64 typo is not used.

Account, XDG, security/observability log, APPDATA/LOCALAPPDATA and all temporary paths remain isolated under the disposable root containing a space. An owner-only empty writable `GIT_CONFIG_GLOBAL` replaces `/dev/null`; fixture-specific isolation stays intact. The original actual macOS cleanup error is retained at `/private/tmp/design-b-t1-focused-native-job-117261498409.log`, SHA-256 `fc94d144581877717c1f5bab1276d7d4a829e79070277f66d75d51924c6c9eec`. No separate Windows cleanup cause is inferred.

Local prerequisite-only proof ran the three exact extracted environment/LFS/verification blocks serially under `rtk proxy bash -e -o pipefail`, with all exits zero. Their wall times were 0.011665, 2.754546 and 0.481209 seconds. Native host was macOS 26.7.1 arm64. Real selected tools were Python 3.13.14, real unsupported Python 3.11.15, fixed CLT/PATH Apple Git 2.54.0, Bash 3.2.57, jq 1.7.1-apple, PowerShell 7.6.7 and RTK 0.51.0 with both processors. No global install ran; existing system Git/Bash/jq differ from hosted Homebrew identities. The fresh arm64 LFS executable SHA-256 `8cb21d1fa650af82a06eaa98c6078303bacf2f101199be3d77ab7370ec712bd0` matches the supplied local binary. Its exact version/path assertions pass. A mode-0600 temporary global config supports real safe-directory add/read/remove and ends empty.

Retained local root: `/private/tmp/design-b-t9c-p-prereq-9zbhimq6`. Receipt `receipt.json` SHA-256 is `bc9c2ecced2ad46317b8b6cdcbf88f2280f4d957d2ac832e62963286732eaa88`; it contains exact block/log hashes, resolved tool paths/hashes and effective isolated variables. The harness is `/private/tmp/design-b-t9c-p-prereq-run.py`. The 3.247420-second block subtotal excludes discovery, Homebrew/setup-python Actions, checkout and every product command; it is not complete workflow timing.

Static proof used vendored PyYAML 6.0.3, `/bin/bash -n` on 26 run blocks, compilation of three Python heredocs, local Markdown links and Git whitespace checks. Static receipt `/private/tmp/design-b-t9c-p-static-receipt.json` SHA-256 is `e97fbe70ae16dbceab993e97769c660ea5713d4063bf013dba248a8a4fda8a93`.

## Actual early hosted run

[Run 38988495837/job 117265372562](https://github.com/japurcell/skills/actions/runs/38988495837/job/117265372562) checked out snapshot `a8e85edcf851936f9943f53ee099305df33a38c8`. Retained full log `/private/tmp/design-b-t9-early-117265372562.log` has verified SHA-256 `ff0f88936786acba1f6c7f27c3ec3698459c3610fa9bebbd0be9d1dae359bf45`. Actual host is macOS 26.6.2 arm64, image `macos-26-arm64` version `20261013.0424.1`.

Every hosted prerequisite passed: real Python 3.11.9 and main 3.13.16, verified arm64 LFS archive/executable above, actual fixed `/Library/Developer/CommandLineTools/usr/bin/git` 2.54.0 Apple Git-157, PATH Homebrew Git 2.56.0, Bash 5.3.20, jq 1.8.2, PowerShell 7.6.6, RTK 0.51.0 and both processors. The hosted LFS executable SHA-256 exactly matches local proof. Checkout post-job successfully writes safe.directory through the writable global config; the prior `/dev/null` lock error is absent.

| Actual full step | Observed result |
| --- | --- |
| Initial generated freshness | Current, 65 files |
| Fixture preflight | 28 tests pass, 219.984 seconds |
| Diagnostic recovery | 17 tests pass, 106.856 seconds |
| Security reporting | 14 tests pass, 103.295 seconds |
| Codex/Copilot/Gemini scanner shells | All pass, including their nested capture suites |
| Exact native Darwin validator | All 12 cases pass with native errno 35 and restored soft limits |
| Checkpoint CLI | 35 tests pass, 27.675 seconds |
| Historical status | 29 tests pass, 21.867 seconds |
| Git gates | 62 tests finish in 58.263 seconds; sole failure is the alias fixture below |

The job stops at that failure. Later LFS/install/lifecycle/cancellation/merger/generator/runner/final freshness steps did not execute. This run is not complete CI acceptance or a measurement of final timeout headroom.

## Bounded fixture repair and targeted proof

The sole failing method was `GateTests.test_selected_index_accepts_verified_macos_system_alias`, at the explicit assertion `fixture did not use a macOS system alias target`. Its repository came from ordinary `setUp` under CI's `/Users/runner/...` TMPDIR, outside `/private/tmp` or `/private/var`; the test never reached its alias gate assertion.

Only this existing method now allocates its repository beneath the verified real `/tmp -> /private/tmp` target. It verifies the actual system alias and resolved selected-index identity, then invokes the same real gate CLI with lexical `/tmp/.../.git/index`. Gate exit zero and exactly one candidate remain required. Runtime, suite-wide `setUp`, all other methods and the existing platform decorator are unchanged. Static AST comparison confirms only this method changed, with 62 test methods retained. Current test-file SHA-256 is `62f15c668403cd555d12ab84b20b652049dbc8d54b69deef7b59a75d6e9e8e16`.

The approved existing public seam was run once before and once after repair:

`rtk proxy python3 scripts/test-scan-secrets-git-gates.py GateTests.test_selected_index_accepts_verified_macos_system_alias`

Both invocations used Python 3.13.14 and the same actual TMPDIR outside both system-alias targets: `/Users/adam/.codex/visualizations/2026/10/15/01a14082-a6b9-7c80-8d84-342460e907c3/t9c-p-alias-4b8vkryj`. Before repair, one test failed with the exact hosted assertion (0.055 test seconds, 0.102454 process wall seconds). After repair, one test passed (0.271 test seconds, 0.318908 wall seconds). No full local replay, runtime change, new skip, relaxed assertion or deliberate source fault was introduced.

Retained proof root `/private/tmp/design-b-t9c-p-alias-proof` contains `red.log` SHA-256 `2eee514bd6a72b38758827a03ed0021896c48d2bde5bb65a472ee18c70a3d08f`, `green.log` SHA-256 `4e70127055e5c46295db82122a0ab018f60fd181ebfe2b405d36defaf52d820e`, `red.json` SHA-256 `82c89d57be8633ee45dce1492dd297491448448ffa4152c0d01abfee5b5bafad` and `green.json` SHA-256 `422079a97fddbf33622833cfe814d4da49dfb6171726a3554d87ad3d47c1215f`.

## Remaining acceptance

The targeted repair is accepted by the primary and the local window is released. Rebase only the three owned files onto the primary's clean integration base; preserve tested bytes and use static comparison instead of an unchanged-input functional replay. The primary will run one actual full integrated macOS workflow and the existing Windows workflow, recording final source identities, results and real timeout headroom. The earlier 30-minute cap remains unproven until that full result. No additional local replay or fault/diagnostic framework is planned. No live-home deployment, trust/enablement changes, background checkpoint, push, PR or release is authorized here. The primary owns the final coordinated knowledge pass.
