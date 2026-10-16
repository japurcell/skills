# Complete the macOS hook-security CI commands

X4 documentation-only preparation, observed 2026-10-16. The current source identity is `df95c107e990fb732563df066a840d37427dce7b` on `codex/design-b-x4`. The task contract is [X4](ExecPlan.md#L492); [T9c-P](ExecPlan.md#L490) remains gated on accepted I4. Accepted prerequisites are T9b `f250a87c3a8f9ff5c665442e55512d7c6e80b2da`, I3-P `cf85ee4c32866844d27dfa3a82d88796dfd34f9c`, and T8a-C `3ff06db82a28764c0e67ee80a1e044886abc8fce`.

This map supplies commands and review pointers, not migration, runtime, CI, native Windows, authenticated host-delivery or deployment acceptance. No product test, generator, installer, benchmark or hosted job ran for X4. The primary owns plan/registry/workflow integration and the one coordinated knowledge pass; this worker owns only this document.

## Preserve the existing workflow

[The job](../../.github/workflows/hooks-posix.yml#L26) uses `macos-latest`, a 30-minute job timeout, explicit Bash, checkout without persisted credentials, Homebrew native prerequisites and Python 3.13. [Tool verification](../../.github/workflows/hooks-posix.yml#L68) requires stable RTK >=0.50.0 with Copilot/Gemini processors. Keep those failure checks. Current workflow SHA-256: `e7948bb0bd1f92516725683eb6e84a369b2a565be33e06b00783fdbf1af221bb`, mode `0644`.

[The initial commands](../../.github/workflows/hooks-posix.yml#L94) are already wired: generated freshness, verification-only fixture preflight, diagnostic recovery, security reporting, then Codex/Copilot/Gemini scanner shells. Keep the scanner pipelines and [exact native validator](../../.github/workflows/hooks-posix.yml#L112). Each shell already calls capture: [Codex](../../scripts/test-codex-hooks-secrets-scanner.sh#L54), [Copilot](../../scripts/test-hooks-secrets-scanner.sh#L315), [Gemini](../../scripts/test-gemini-hooks-secrets-scanner.sh#L76). Do not add a standalone capture invocation or duplicate its output into the same evidence log. The validator requires exactly four distinct mode/status cases per provider, native Darwin errno, strict fields/types and restoration observations; a generic capture PASS cannot replace it. [T9b](t9b-evidence.md#L43) proves pipeline exit propagation and ten malformed/missing-evidence controls in its earlier scope.

Use separate sequential steps or sequential commands, retaining `bash -e -o pipefail` and `rtk proxy`. If new logging uses `tee`, preserve pipefail so a successful logger cannot hide a failing suite. Never use `continue-on-error`. Keep the three scanner evidence log names unchanged.

## Add the remaining public commands after I4

Working directory for every command is the final integrated repository root. These are full commands, not selected-method substitutes. Add them to the macOS job alongside the existing steps; run them serially against frozen final inputs. All Python commands use the same verified Python 3.13 first on PATH.

| Add command | Public behavior and source entry point |
| --- | --- |
| `rtk proxy python3 scripts/test-scan-secrets-cli.py` | Standalone checkpoint help/streams/exits, budgets, hostile environment, immutable input and cancellation: [CheckpointTests](../../scripts/test-scan-secrets-cli.py#L19). |
| `rtk proxy python3 scripts/test-scan-secrets-status.py` | Read-only historical status, strict/redacted records, storage races and no scan/network side effects: [StatusTests](../../scripts/test-scan-secrets-status.py#L19). |
| `rtk proxy python3 scripts/test-scan-secrets-git-gates.py` | Actual commit/push enforcement, full changed staged files, outgoing history/ref transactions, incomplete refusal and installed closure: [GateTests](../../scripts/test-scan-secrets-git-gates.py#L17). |
| `rtk proxy python3 scripts/test-scan-secrets-lfs.py` | Actual recording-endpoint upload, exact payload bytes, zero-transfer rejection, ordered hooks and cancellation: [LFSTests](../../scripts/test-scan-secrets-lfs.py#L78). |
| `rtk proxy python3 scripts/test-install-repo-gates.py` | Read-only preview plus real activation/uninstall, ownership, recovery, worktrees, original hooks and standard LFS composition: [RepositoryPreviewTests](../../scripts/test-install-repo-gates.py#L22). |
| `rtk proxy python3 scripts/test-install-scan-secrets.py` | Neutral install, genuine prior-release upgrades, source-free execution, trusted closure and real main installers: [InstalledScannerTests](../../scripts/test-install-scan-secrets.py#L19). |
| `rtk proxy python3 scripts/test-scan-secrets-lifecycle.py` | Full final T8b migration/lifecycle suite. The [current integrated entry](../../scripts/test-scan-secrets-lifecycle.py#L16) is still the older 14-method suite; refresh from accepted T8b before running. |
| `rtk proxy python3 scripts/test-scan-status-cancellation.py` | Ordinary SIGTERM/SIGINT, closed output, consumed incomplete input and finished-root descendant cleanup: [CancellationTests](../../scripts/test-scan-status-cancellation.py#L17). |
| `rtk proxy python3 scripts/test-install-codex-hooks.py` | Public Codex configuration-merger contract; run with final T8b merger source. [Entry](../../scripts/test-install-codex-hooks.py#L1). |
| `rtk proxy bash scripts/test-install.sh` | Complete real Bash installer fixture contract, including generated/provider assets and migration. [Fixture entry](../../scripts/test-install.sh#L10). |
| `rtk proxy pwsh -NoProfile -File scripts/test-install.ps1` | Complete real PowerShell installer on macOS. [Contract and host-specific skips](../../scripts/test-install.ps1#L1). This does not establish native Windows/NTFS support. |
| `rtk proxy python3 scripts/test-generate-hooks.py` | Generator behavior/count/closure assertions, beyond the already wired freshness command. [Entry](../../scripts/test-generate-hooks.py#L1). |
| `rtk proxy python3 scripts/test_test_all.py` | Exact maintained-suite registration and runner stream/cancellation/error behavior. [Registry coverage](../../scripts/test_test_all.py#L86). |

Finish with `rtk proxy python3 scripts/generate-hooks.py --check` against unchanged final source. Do not run `--write` in CI to conceal drift. Installer/lifecycle suites perform generation or installation only inside their disposable fixtures; invoking the test interface is distinct from installing the real checkout into a user's home.

[The registry](../../scripts/test-all.py#L20) already contains all these standalone commands, including cancellation, both real installer commands and generator/runner tests. Static AST counting gives 61 tuples at this identity. [Assertions](../../scripts/test_test_all.py#L119) require the maintained path set, equal cardinality and explicit command shapes for the core CLI/gate/installation group. Cancellation is included in the expected set. No registration edit is presently needed. Registry SHA-256: `c5c534c9e9430c0a06eb34c5519b5718008fff82526dc5b95c3f617603bad79a`; assertion-file SHA-256: `711f44c44bda33e88324a3b8c5acaeaa7f5f84721fd320b394d2f5a36c939b71`.

`test-all.py` has only `--list`, no subset flag, and runs broader unrelated suites. Do not add an aggregate run on top of these focused steps: it would repeat scanner/capture and installation work. Its [aggregate prerequisites](../../scripts/test-all.py#L187) also include `flock` and `sqlite3`, beyond the current workflow's explicit native package list. Any genuinely new standalone suite requires one registry row plus exact coverage assertions, with primary ownership.

## Resolve prerequisites and isolate execution

Preserve [the workflow's disposable environment](../../.github/workflows/hooks-posix.yml#L47), including the path containing a space. It pins HOME, USERPROFILE, CODEX_HOME, TMPDIR, all three XDG roots, scanner/Guardian/audit/observability logs, OBSERVABILITY_TESTING, and Git global/system/prompt isolation. For local replay, create an unused temporary root and export the same effective variables before any suite. GITHUB_ENV/GITHUB_PATH are Actions handoff files; writing them in a local shell does not itself change later local commands. Select Python 3.13 on PATH before installers, record resolved paths/versions, and keep every account-specific destination inside the temporary root. Pin APPDATA/LOCALAPPDATA and TEMP/TMP there if present in the local environment; clear inherited installer selection such as INSTALL_FOREST_SERVICE_SKILLS. Do not repurpose the working agent's own HOME/CODEX_HOME variables in orchestration.

Three additions need explicit prerequisite treatment before T9c-P can reproduce the full command set:

1. **Exact LFS tool.** [LFS binding](../../scripts/test-scan-secrets-lfs.py#L218) requires `git-lfs/3.8.0 ` and binds its bytes/version. [Repository installation](../../scripts/test-install-repo-gates.py#L253) uses TEST_GIT_LFS or a workstation-specific `/tmp/design-b-lfs-3.8.0/...` default, rather than PATH lookup. Current `brew install git-lfs` alone does not prove this requirement. Provision verified Git LFS 3.8.0 in the disposable tool area, export absolute TEST_GIT_LFS for both suites, and verify its version/hash. No workstation `/tmp` path is a hosted dependency. If fixture-version support changes, route that product/test change to its owner and rerun it; do not weaken the assertion as CI preparation.
2. **Real unsupported interpreter.** [The negative case](../../scripts/test-install-repo-gates.py#L1087) needs a real Python <3.12. Provision an explicit old interpreter and export TEST_UNSUPPORTED_PYTHON, then restore Python 3.13 precedence for the suites and real installers. Verify the old executable's version; a shim is not the required negative. Do not assume the runner's Apple Python remains old enough.
3. **Darwin fixed Git path.** [Repository fixtures](../../scripts/test-install-repo-gates.py#L19) pin `/Library/Developer/CommandLineTools/usr/bin/git` even when Homebrew Git is on PATH. Check that executable exists and record its version separately. An Xcode-selected runner need not share this workstation layout. If absent, the fixture's supported selection seam needs an owner-approved source change before wiring can pass; a PATH change alone cannot fix that constant.

LFS tests bind a loopback recording HTTP endpoint; [I3-P](i3-p-evidence.md#L53) records sandbox socket denial separately from scoped successful loopback runs. Local execution needs loopback sockets and process inspection/signaling for owned fixture PIDs/groups. Missing prerequisites or sandbox denials remain incomplete validation, not successful skips. Native Darwin capture must execute on Darwin. PowerShell 7, Bash, jq, Git and RTK processors remain required; the neutral suite explicitly [requires PowerShell](../../scripts/test-install-scan-secrets.py#L40). Offline prior-release [archives and provenance](../../scripts/test-install-scan-secrets.py#L55) avoid relying on shallow-checkout historical Git objects.

Keep generator checks, installer suites, migration fixtures and timing runs serialized. [The plan's integration rule](ExecPlan.md#L508) notes generator tests compare whole-checkout state. Do not edit final canonical inputs while any proof is running. Keep per-step logs, source hashes, interpreter/tool identities, command exit codes and elapsed wall time. Check that all deliberate faults are absent before the final clean run.

## Refresh provisional T8b inputs

Read-only observations below came from `/Users/adam/.codex/worktrees/design-b-t8b/skills` while the owner held its final candidate frozen for serial validation. Its base checkpoint is `e3d1dee8a2334eac3323deb60506d095336888e8`, but lifecycle and merger bytes have later uncommitted fixes. Do not label checkpoint bytes as the final candidate. The observed lifecycle candidate contains 32 test methods: genuine old-template upgrade, idempotent real PowerShell upgrade, ordered recovery, pinned-old-interpreter/removed-event migration, disabled-state preservation, echo/substitution/PowerShell ambiguity controls, FIFO refusal, duplicate JSON refusal, and source-free installed status. No result for those methods is asserted here.

T8b source hashes below identify observations only. Modes are `0755` for Python/shell scripts and `0644` for JSON. Fixture names share `scripts/fixtures/provider-hooks-pre-status/`.

| Provisional path | Observed SHA-256 |
| --- | --- |
| `scripts/test-scan-secrets-lifecycle.py` | `57a9cb8b6c7d6a987d2ba5891e6e41256b1bfd934cc495aa127adf38ae33f2a6` |
| `scripts/install-codex-hooks.py` | `ab896fad81b3206412ab76dcabeb8b0637692b1a27d110de17a4c5d6868a17ab` |
| `scripts/install-provider-hooks.py` | `554ad7a9bcdd7ea5a006235d9170ea464f16d596fbf33e9cc2eaf4379714aad4` |
| `.codex/global-hooks.json` | `e36f7d84f3845ef20de8feb6a0c4bcc803bd93452baa0552e82237e69afa7a7e` |
| `.copilot/hooks/hooks.json` | `e8228b9a31fa6813a1b94bef1f35e87e4ee8637e54c82e869f8085629cc4e5cc` |
| `.gemini/global-settings.json` | `73b93c66397830f961f999ba2b290b812415598c74a2db62ac94ac6072d53c44` |
| `scripts/test-install.sh` | `240d54a97cfaf93dedf8437dc2a8986e155b1f8d007fbeff4107abd2f9830cf6` |
| `scripts/test-install.ps1` | `3870d09a1760b7923f5833faed4f7d33ed8dda555650eeaa1b3565b90ca71567` |
| `codex.json` | `15d1f58f3c245e1cc514b1e3e0992d131cdac249f55f59ace10b5750ef17bb08` |
| `copilot.json` | `a05b4871cdf151486f1f2e4a2a4f2e05bbefb580cf43dc4649529ef54a11ccac` |
| `gemini.json` | `6686efb4dc6477391c0ae2347ca87618efff1843553c252ada102da3d0bf221e` |
| `provenance.json` | `e08bd1bbe5fdb399997b9487d94496935b977d144928bb65ee656e78d57e820b` |

Refresh all affected identities, registration assertions, fixtures and line references after accepted T8b/I4 integration. The provisional templates register status at Codex Stop, Copilot agentStop and Gemini AfterAgent. The refined pinned-old-command test removes Copilot sessionEnd/Gemini SessionEnd from its replacement template before migration; this matters because the production template may retain unrelated handlers at those events. Exact ownership, unrelated settings/handlers and disabled/trust intent must survive. The older integrated lifecycle SHA-256 is `a889bb89ce85fc4156f316d45f512ed71d36b9cedf52389f48984f917eafd852`; the accepted focused cancellation SHA-256 is `1a3853d0a248ca6bb4d0a50124a7623737cf3c78284fc5c00ccc2f8c191b455d`. T9c-P must rerun the actual final full commands, not reuse these observations as acceptance.

## Assess the 30-minute budget without inventing a combined measurement

The following are retained historical observations on local macOS, with their original build/test scope. They are neither a hosted runner prediction nor a measured combined workflow. Values from different revisions/interpreters must not be relabeled as one final run.

| Historical command scope | Seconds | Retained evidence |
| --- | ---: | --- |
| Initial preflight 22 / recovery 15 / reporting 14 | 89.872 / 63.968 / 71.885 | [T9a](t9a-evidence.md#L39), preflight/recovery reused from I1; reporting 3.14.6 |
| CLI 35 / status 29 / gates 62 | 17.780 / 15.187 / 47.675 | [T6 compatibility](t6-evidence.md#L80), 3.14.6 |
| LFS full 43 | 64.877 | [T6](t6-evidence.md#L74), 3.13.14 |
| Repository preview/activation/recovery 60 | 58.576 | [T7b-P](t7b-p-evidence.md#L94), final scoped 3.13.14 |
| Neutral installer full 25 | 52.795 wall | [T7-U](t7-u-evidence.md#L57), 3.13.14 |
| Older lifecycle 13 / full Bash / full PowerShell | 18.879 / 76.629 / 281.658 | [T8a](t8a-evidence.md#L42), 3.13.14; lifecycle predates final 14/32-method shapes |
| Cancellation 5 / generator 26 / runner 14 | 1.805 / 16.639 / 12.883 | [T8a-C](t8a-c-evidence.md#L31), 3.13.14; lifecycle selection there is only five methods |
| Codex merger test | 0.205 | [T8a](t8a-evidence.md#L50), 3.13.14, before final T8b merger |

Arithmetic illustration only: the listed command groups excluding lifecycle total about 872 seconds (14.5 minutes), mixing historical scopes. This excludes all three scanner shells/native validation, checkout/tool downloads, the new full lifecycle suite and runner variability. The retained [T9b scanner proof](t9b-evidence.md#L45) establishes serial success but supplies no elapsed wall value to fill that gap. No measured combined runtime exists here. I3-P's [capacity and separate profiling](i3-p-evidence.md#L27) are different workloads; do not sum them into CI timing or add benchmarks to functional CI merely to estimate it.

Thirty minutes is a provisional cap, not demonstrated adequate headroom. The old PowerShell suite alone needed a successful 900-second outer allowance after a 240-second orchestration interruption and completed around 281 seconds; [that interruption](t8a-evidence.md#L40) was not a suite assertion failure. After I4, time every actual final command serially under the effective workflow environment, retain the total including native prerequisite setup where observable, then set the job timeout with explicit margin for hosted variability. Increase a justified job/outer allowance rather than weakening product deadlines or tests. A local clean sequence still leaves hosted duration and V1 CI links/branch protection open.

## Reproduce failure controls locally after I4

T9c-P owns these executions, not X4. First validate YAML with the existing vendored loader pattern, shell syntax and the complete command order. Extract the final run blocks unchanged and execute through `rtk proxy bash -e -o pipefail` with the isolated environment above. Save exact source/modes before any fault, use independent disposable checkout copies for the controls, and never patch the real checkout or home.

1. Follow [T9a's exact recovery control](t9a-evidence.md#L46): in the disposable copy replace the first `self.assertEqual(rows[0]["mode"], mode)` with the deliberate marker expectation. Recheck that the current assertion still exists exactly once at the selected location; otherwise identify its current equivalent explicitly. Run the full final `rtk proxy python3 scripts/test-hook-diagnostic-recovery.py`, require nonzero exit and intended mode failures. Historical six-failure/15-method output is provenance, not the expected current suite count.
2. In another disposable copy append the documented drift comment to `.codex/hooks/scan-secrets.py`. Run the full final `rtk proxy python3 scripts/generate-hooks.py --check`; require nonzero exit naming that drifted asset. Do not demand an undocumented repair hint and do not generate away the fault before observing failure.
3. Preserve [T9b's native missing-case control](t9b-evidence.md#L59): copy final real scanner logs, remove one Codex native event, run the exact final validator, and require missing-evidence failure. Keep real logs untouched. Recheck pipeline propagation with a disposable fixture exiting 37 if pipeline code changed; `tee` must retain that exit. Final unmodified logs must pass all 12 cases.

Discard fault copies, compare final source/modes against frozen identities, run the complete final clean workflow sequence serially, and record each actual outcome before accepting local wiring. Keep failures attributable: prerequisite denial, controlled red, product failure, clean rerun and actual hosted result are distinct evidence. Stop at this documentation boundary; source delivery, native support and external acceptance remain with their named tasks.
