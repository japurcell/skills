# T9c-P macOS CI wiring evidence

Status: source preparation and local prerequisite proof only, 2026-10-16. The primary granted an exclusive prerequisite-only local window after W2 drained. The three extracted environment, LFS provisioning and tool-verification blocks pass. No product suite, generation, installation, benchmark, deliberate source fault or hosted job ran for this checkpoint. Full local functional acceptance and actual hosted acceptance remain open.

## Scope and accepted inputs

This worker owns only `.github/workflows/hooks-posix.yml`, strictly necessary registry wiring and this evidence file. The primary owns the shared [ExecPlan](ExecPlan.md), source-map links, final source composition, CI transport, integration and coordinated knowledge pass. No private T1 source is imported. W2 retains native runtime/generator/installer source ownership. This worker owns only the prerequisite window; product execution requires a new primary grant. No product security, trust or enablement policy changes, real-home deployment, background work, direct push, PR or release is included.

The clean starting commit is `fa58ef356923644b9850986e82cb85e9c3aea57e` on private branch `codex/design-b-t9c-p`. Accepted prerequisites supplied by the primary are T9b `f250a87c3a8f9ff5c665442e55512d7c6e80b2da`, I4 `cebf04eaefdce00af366d3140bce816b86cab6bf` and R8 `fd622fe9452cabb4155a39a423fc1eb090a4f6ba`. R8's hosted result is separately scoped evidence, not a T9c-P result. T1-CI2 remains unresolved and private; a full green and focused non-reproduction do not explain its earlier incomplete scan. Final preflight proof must use the primary's reconciled source rather than silently importing that private candidate.

The accepted [macOS source map](macos-ci-source-map.md) has SHA-256 `9f065476966af59bcdecc19f354ea5f9d5cf59860be74b00dc05d0926fa90db0`. Its historical prerequisite/status prose and plan anchors are not current authority. Current lifecycle contains 32 test methods. Its lifecycle, merger, provider templates and historical fixture hashes match the formerly provisional map rows. Current `test-install.ps1` includes accepted W0 work and differs from the provisional row. All requested commands are already among the registry's 61 unique tuples; registry source and its existing coverage assertions remain unchanged.

## Prepared workflow behavior

The draft preserves checkout credential isolation, Python 3.13 precedence, stable RTK processor checks, generated freshness, full fixture preflight/recovery/reporting, all three scanner shells and their original log paths, and the exact 12-case native Darwin validator. The scanner shells already invoke capture; no standalone aggregate capture or aggregate `test-all.py` run is added. Every new standalone public command appears exactly once and already exists in the maintained registry. Bash steps retain the explicit Actions Bash shell with `-e` and `-o pipefail`; no `continue-on-error` is introduced.

Preparation adds a real secondary Python 3.11 through `actions/setup-python@v7` with `update-environment: false`, exports its absolute `python-path` as `TEST_UNSUPPORTED_PYTHON`, then selects Python 3.13 for ordinary commands. It replaces Homebrew's unpinned LFS dependency with an architecture-selected official Git LFS 3.8.0 archive, checks the published SHA-256 before extraction, exports absolute `TEST_GIT_LFS` and places that binary first on PATH. Verification checks Python identities, exact LFS version/path, the fixture's actual Darwin Git path and existing native tool/RTK requirements.

The disposable environment retains the directory containing a space and isolates HOME, USERPROFILE, CODEX_HOME, TMPDIR, all XDG roots and security/observability logs. It additionally isolates TEMP/TMP and APPDATA/LOCALAPPDATA and clears inherited optional installer selection. A new owner-only empty writable temporary Git global config replaces `/dev/null`; fixture-specific Git isolation is unchanged.

## Verified prerequisite sources

The [official Git LFS v3.8.0 release](https://github.com/git-lfs/git-lfs/releases/tag/v3.8.0) and [expanded assets](https://github.com/git-lfs/git-lfs/releases/expanded_assets/v3.8.0) publish the Darwin ZIP assets and hashes below. Asset links were followed to verify the direct download URLs. The web tool refused the binary redirect; subsequent approved local provisioning through the exact workflow block downloaded the arm64 ZIP and verified its published hash before extraction, as recorded below.

| Architecture | Official archive SHA-256 |
| --- | --- |
| `git-lfs-darwin-amd64-v3.8.0.zip` | `f1c17aeca0b4eaab9ea606226477dbed3b84b56fe0811a9f967d2ea2b2393c53` |
| `git-lfs-darwin-arm64-v3.8.0.zip` | `caff76a7d070d8160c89bc39b6e85d98f24135b6fed038a3b4de2590d25102d8` |

The URLs are `https://github.com/git-lfs/git-lfs/releases/download/v3.8.0/git-lfs-darwin-ARCH-v3.8.0.zip`, selecting only `amd64` or `arm64`. The supplied `/tmp/design-b-ci-prerequisite-sources.json` receipt was independently read and compared with those official hashes; receipt SHA-256 is `ff0a92d9611731cbf2b98a927730924b50955e7ece71eced41b861b8d2c28624`. The initial assignment's arm64 digest typo is not used. The newly provisioned binary and the supplied `/tmp/design-b-lfs-3.8.0/git-lfs-3.8.0/git-lfs` are byte-identical, SHA-256 `8cb21d1fa650af82a06eaa98c6078303bacf2f101199be3d77ab7370ec712bd0`. No LFS fixture suite ran.

[Setup Python v7 advanced usage](https://github.com/actions/setup-python/blob/v7/docs/advanced-usage.md) documents the absolute `python-path` output and environment-preserving `update-environment: false`. The GitHub Contents API was unavailable through the web tool; the versioned official source page was read instead. [Checkout v7](https://github.com/actions/checkout/blob/v7/README.md) documents global `safe.directory` writes. This supports using a writable isolated config file; actual post-job success remains a hosted observation to collect.

The actual focused hosted log `/private/tmp/design-b-t1-focused-native-job-117261498409.log` has verified SHA-256 `fc94d144581877717c1f5bab1276d7d4a829e79070277f66d75d51924c6c9eec`. At cleanup it records a global safe-directory write, `error: could not lock config file /dev/null: Permission denied`, and failed safe-directory initialization. This is the concrete macOS reproducer for the temporary global-config change. It does not attribute any separate Windows cleanup failure.

`scripts/test-install-repo-gates.py:19` selects `/Library/Developer/CommandLineTools/usr/bin/git` on Darwin. That executable executes locally as `git version 2.54.0 (Apple Git-157)`. The workflow now explicitly checks it before suites; availability on the actual hosted runner is unverified. A missing path must fail visibly. The primary explicitly retains ownership reconciliation for a portability-source repair after actual evidence; this worker has not changed the fixture.

## Static verification observed

Vendored PyYAML 6.0.3 loads the workflow successfully from `scripts/vendor/yaml/`. `/bin/bash -n` accepts all 26 run blocks. Static comparison proves all eight original required test/freshness/validator steps are exact and each of the 13 added full public commands is present once in both workflow and registry. No standalone capture or aggregate invocation and no `continue-on-error` is present. The exact native validator run-block SHA-256 remains `3ca5e33ec2cbef943c7b3854d9cd4e955cbeb5041e1021ce97e37e045c2f2f18`.

Static receipt `/private/tmp/design-b-t9c-p-static-receipt.json` has SHA-256 `e97fbe70ae16dbceab993e97769c660ea5713d4063bf013dba248a8a4fda8a93`. It records the base, workflow, vendored parser identity, command counts and refreshed inputs below. These observations establish parsing and wiring only.

| Current input | Mode | SHA-256 |
| --- | --- | --- |
| `.github/workflows/hooks-posix.yml` | `0644` | `bbed38d1698ae9c14044ca0973c73b4c7d5d75970b1b265862a507b2ee18a4bc` |
| `scripts/test-all.py` | `0755` | `c5c534c9e9430c0a06eb34c5519b5718008fff82526dc5b95c3f617603bad79a` |
| `scripts/test_test_all.py` | `0644` | `711f44c44bda33e88324a3b8c5acaeaa7f5f84721fd320b394d2f5a36c939b71` |
| `docs/hook-resilience-design-b/macos-ci-source-map.md` | `0644` | `9f065476966af59bcdecc19f354ea5f9d5cf59860be74b00dc05d0926fa90db0` |
| `scripts/test-scan-secrets-lifecycle.py` | `0755` | `57a9cb8b6c7d6a987d2ba5891e6e41256b1bfd934cc495aa127adf38ae33f2a6` |
| `scripts/install-codex-hooks.py` | `0755` | `ab896fad81b3206412ab76dcabeb8b0637692b1a27d110de17a4c5d6868a17ab` |
| `scripts/install-provider-hooks.py` | `0755` | `554ad7a9bcdd7ea5a006235d9170ea464f16d596fbf33e9cc2eaf4379714aad4` |
| `.codex/global-hooks.json` | `0644` | `e36f7d84f3845ef20de8feb6a0c4bcc803bd93452baa0552e82237e69afa7a7e` |
| `.copilot/hooks/hooks.json` | `0644` | `e8228b9a31fa6813a1b94bef1f35e87e4ee8637e54c82e869f8085629cc4e5cc` |
| `.gemini/global-settings.json` | `0644` | `73b93c66397830f961f999ba2b290b812415598c74a2db62ac94ac6072d53c44` |
| `scripts/test-install.sh` | `0755` | `240d54a97cfaf93dedf8437dc2a8986e155b1f8d007fbeff4107abd2f9830cf6` |
| `scripts/test-install.ps1` | `0755` | `3c6dd01f06c637c9f6ca8dd756572e4bf7b49701149ba55f99e9c2909d8fa934` |
| `scripts/test-install-repo-gates.py` | `0755` | `b63af0a8343e07e182e89295d7ceef38e60c2b73d24d2081cd33625a5e2fdf25` |
| `scripts/fixtures/provider-hooks-pre-status/codex.json` | `0644` | `15d1f58f3c245e1cc514b1e3e0992d131cdac249f55f59ace10b5750ef17bb08` |
| `scripts/fixtures/provider-hooks-pre-status/copilot.json` | `0644` | `a05b4871cdf151486f1f2e4a2a4f2e05bbefb580cf43dc4649529ef54a11ccac` |
| `scripts/fixtures/provider-hooks-pre-status/gemini.json` | `0644` | `6686efb4dc6477391c0ae2347ca87618efff1843553c252ada102da3d0bf221e` |
| `scripts/fixtures/provider-hooks-pre-status/provenance.json` | `0644` | `e08bd1bbe5fdb399997b9487d94496935b977d144928bb65ee656e78d57e820b` |

## Local prerequisite proof observed

The primary granted a prerequisite-only exclusive window after W2 drained. A temporary harness extracted the three final run blocks unchanged from workflow SHA-256 `bbed38d1698ae9c14044ca0973c73b4c7d5d75970b1b265862a507b2ee18a4bc` and ran them serially through `rtk proxy bash -e -o pipefail`. The fresh root was `/private/tmp/design-b-t9c-p-prereq-9zbhimq6`, on native macOS 26.7.1 arm64. The harness supplied existing real interpreter paths instead of executing hosted `setup-python` Actions, and did not execute the Homebrew bootstrap or install anything globally. The temporary environment selected Python 3.13 before ordinary commands and kept the real 3.11 executable in `TEST_UNSUPPORTED_PYTHON`.

| Exact workflow block | Exit | Wall seconds | Retained log SHA-256 |
| --- | ---: | ---: | --- |
| Prepare disposable test environment | 0 | 0.011665 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| Provision verified Git LFS 3.8.0 | 0 | 2.754546 | `0e64ddcef31f5b883bbdd3c0647fbc9e8769f1d51dd804b6fbd429b26112279a` |
| Verify native tools and stable RTK processors | 0 | 0.481209 | `343be16edb9dee9c22a7e15befdd142e0fcdd7e2ce376096ee01a02e3c42d3da` |

Logs are respectively `environment.log`, `lfs.log` and `verify.log` under that retained root. The exact-block subtotal is 3.247420 seconds; it excludes interpreter discovery, Homebrew/setup-python Actions, checkout, config-write probes, tool hashing and every product command. It cannot establish complete CI timing or headroom.

The arm64 ZIP download passed published SHA-256 verification before extraction. The exact exported `TEST_GIT_LFS` is `/private/tmp/design-b-t9c-p-prereq-9zbhimq6/hook security/tools/git-lfs-3.8.0/git-lfs-3.8.0/git-lfs`; both direct execution and `git lfs version` report `git-lfs/3.8.0 (GitHub; darwin arm64; go 1.27.0; git aece9221)`. The selected PATH binary resolves to that exact file. All isolated account/log/cache/temp paths resolve beneath the fresh root. `GIT_CONFIG_GLOBAL` is an initially empty mode-0600 regular file; real `git config --global --add safe.directory`, `--get-all safe.directory` and `--unset-all safe.directory` succeed against it, leaving zero bytes. This verifies local writability, not actual checkout post-job execution.

Actual executable identities are below. Every SHA-256 covers the resolved file bytes. Local Homebrew Git/Bash/jq formulas are absent; their existing system counterparts pass the workflow's current verification requirements. These local identities are explicitly different from anticipated hosted Homebrew tools. No compatibility or suite result is inferred from versions alone.

| Tool and observed version | Selected executable | Resolved-file SHA-256 |
| --- | --- | --- |
| Main Python 3.13.14 | `/Users/adam/.pyenv/versions/3.13.14/bin/python3` | `8cd011b1e3d3ea63445a00e1ee1ca7114e2aa142313ec597f238e632acbb49a1` |
| Real unsupported Python 3.11.15 | `/Users/adam/homebrew/opt/python@3.11/bin/python3.11` | `ff3d2d712d613f41a59b310eb53b26f6c4fa9142fde21016ec60312d24a75ec7` |
| PATH Git 2.54.0 Apple Git-157 | `/usr/bin/git` | `5b1ddb7e9c11b87a034fc88b212e8ac243cfe2b4db696d767aa44c79595fc09a` |
| Fixture Git 2.54.0 Apple Git-157 | `/Library/Developer/CommandLineTools/usr/bin/git` | `a73bf622a2e470d5d57a4b1d5aef1e8680e67278018d4858a2f93825b7d595c7` |
| Bash 3.2.57(1)-release | `/bin/bash` | `67e853b740606c0cb92fc8b7186a98d327d783f7e7cd911773bb83f73f3d6583` |
| jq 1.7.1-apple | `/usr/bin/jq` | `06fa2856c80e61b6f2a6830352a725f58a8a7c6d61c156771f5bdc259a1c677f` |
| PowerShell 7.6.7 | `/Users/adam/homebrew/opt/powershell/bin/pwsh` | `eca8d40a019522d13dbf66fe9261f5f591a5ee0c2dba84e3b1d69e39d9a99960` |
| RTK 0.51.0 | `/Users/adam/homebrew/opt/rtk/bin/rtk` | `02866e65968c0359b19495a5dc2d3ec643a1553fdd1c83c0ad33a8ad33bac3c9` |

The real 3.11 resolves to `/Users/adam/homebrew/Cellar/python@3.11/3.11.15_4/Frameworks/Python.framework/Versions/3.11/bin/python3.11`. Apple Python was independently observed as 3.9.6 and not selected for this proof. RTK's stable-version and both Copilot/Gemini processor assertions pass.

The retained prerequisite harness is `/private/tmp/design-b-t9c-p-prereq-run.py`. Its receipt `/private/tmp/design-b-t9c-p-prereq-9zbhimq6/receipt.json` has SHA-256 `bc9c2ecced2ad46317b8b6cdcbf88f2280f4d957d2ac832e62963286732eaa88` and contains exact extracted-block hashes, logs, effective isolated variables, resolved tool paths and hashes, and config probe result. Temporary prerequisite artifacts remain available for primary inspection and do not belong in the Git commit.

## Required execution window and remaining proof

The prepared local replay groups are sequential: prerequisites and freshness; full fixture preflight/recovery/reporting; all three scanner shells plus the unchanged validator; checkpoint CLI/status/Git gates/LFS; repository and neutral installation; full lifecycle/cancellation/Codex merger; complete Bash and PowerShell installers; generator behavior/runner/final freshness. Each public command must run in full, through the final extracted workflow blocks, against frozen final source and real verified prerequisites. Retain exact effective environment, source SHA/modes, tool/interpreter paths and versions, per-command output/exit/wall time and native scanner logs. Do not run the broader aggregate or duplicate capture.

After the primary grants a separate full functional window and reconciles final input composition, first retain controlled nonzero recovery and generated-drift results in independent disposable checkout copies using the source-map controls. Preserve original copies/modes. Recheck the missing-native-case failure using copied real scanner logs. The existing scanner pipelines are unchanged; their original exit-propagation proof is retained, with any renewed control executed only in a disposable fixture. Remove all deliberate faults and verify the final clean source/modes before the complete serial clean sequence. No production file may carry a deliberate fault into commit or integration.

The retained 30-minute timeout is provisional at this preparation checkpoint. Historical 14.5-minute arithmetic excludes important suites and setup and is not adequate justification. Measure final full local command times and actual hosted setup/job duration/headroom before accepting the timeout or justifying independently complete job grouping. No test deadline or assertion may be relaxed to fit CI.

Local prerequisite proof is complete within the observed scope. Open proof: actual hosted bootstrap/setup-python/archive provisioning and fixed Git path; actual checkout post-job cleanup; full local commands and failure controls on reconciled frozen inputs; final functional source comparison; actual primary-owned exact-source hosted full run and measured headroom. The current two-file prerequisite checkpoint is prepared for a clean private commit and early primary-owned hosted prerequisite transport, without importing private T1 files. Primary performs integration and the single final knowledge-maintenance pass after all owners finish. Local YAML success never substitutes for hosted acceptance.
