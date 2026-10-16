# T8b exact provider registration migration evidence

Date: 2026-10-16. Private branch: `codex/design-b-t8b`. Prepared base: `0bf18e9764b9a2e00763e089af2c41a7710f6141`. Prerequisites are accepted T8a `6151ba5cb7aaaf5ac0da5e48d0ff2fe5faa1efb7` and I3-P `cf85ee4c32866844d27dfa3a82d88796dfd34f9c`.

T8b implementation and its final local frozen validation are complete; primary review and integration remain separate. This receipt covers source/public CLI behavior and disposable installed workflows on macOS. No global safety coverage, authenticated provider delivery or native Windows acceptance is claimed.

## Delivered behavior and ownership

The installer-only `hooks/registrations.py` lists desired provider handler/event identities and explicitly retired scanner/event identities independently of template event membership. Exact supported historical command forms and exact pinned installed launches establish ownership. A missing previous interpreter does not erase the recorded exact launch identity. Unrelated paths sharing a basename survive; matching owned paths with conflicting command pairs or an additional executable override refuse migration without rewriting the configuration.

Codex keeps synchronous Guardian at `PreToolUse` and selects the bounded historical status action at `Stop`. Copilot uses `agentStop`, with the existing status adapter's separately tested VS Code `Stop` response. Gemini uses `AfterAgent`, retaining logical name `scan-secrets` so an existing `hooks.disabled` name continues to apply. Old full scanners retire from the former tool and stop/session-end events. Observability, bell, RTK forwarding, independent validators and unrelated nested settings remain independently owned.

Both merger CLIs validate the exact deployed self-contained `scan-status.py` before activating a status registration. They use initial `-I -S -B` pinned launches. Existing platform installers already deploy the neutral bundle before provider copies and copy each provider's status asset before its configuration merge; T8b adds activation-time exact-byte/link validation rather than changing that ordering. Per-config updates are atomic with retained semantic backups. The multi-provider operation is ordered, not globally atomic. A controlled second-provider failure leaves the first provider's new registration usable with deployed assets and the remaining previous configuration recognizable; rerunning the same installer completes the migration.

A stable private `<config>.install-lock` uses immediate kernel locking for cooperating writers; interruption releases the kernel lock and the file is retained. Drift observed before promotion is refused. This supplies no arbitrary direct-editor compare-and-swap guarantee. Hard-linked configuration repair replaces the destination inode instead of chmodding or overwriting the external peer. Linked configuration ancestors and linked status assets are refused before migration mutation. macOS's fixed `/var` and `/tmp` aliases to `/private` remain supported for disposable fixture paths.

Repository Git gates remain an explicit owner choice through `scan-secrets hooks install --repo PATH`. Provider installation does not activate repositories or authorize publication. User-global Copilot `disableAllHooks`, Codex enable/trust data and Gemini disabled names remain owner-controlled. No real home was deployed, and no enablement/trust setting was changed.

## Genuine public red and green observations

All commands run from the private worktree and use `rtk proxy`; generated refreshes use only the canonical generator. The human already confirmed these public seams. Tests retain positive replacement operation rather than relying on scanner absence.

1. `python3 scripts/test-scan-secrets-lifecycle.py LifecycleTests.test_gemini_disabled_names_survive_status_upgrade` first failed through the real Bash installer with `Gemini install failed: Existing hooks.disabled[0] must be an object`. The valid old settings contained `hooks.disabled: ["scan-secrets", "user-validator"]`. After schema distinction, the same public flow reached its second genuine red: no status handler was registered (`0 != 1`). The migration then passed, preserving the disabled logical name and nested custom setting and executing the source-free installed status action to report `last clean`. The installed diagnostic CLI now also checks that these registrations remain observable.
2. `LifecycleTests.test_extra_executable_override_refuses_migration_without_mutation` first failed because the merger returned 0 for an exact Copilot scanner pair plus an unrelated `command` executable override. Checking the executable-field/type shape before ownership admission gives exit 1, an `Ambiguous` diagnostic, identical destination bytes and no semantic backup.
3. `LifecycleTests.test_provider_migration_cooperating_lock_preserves_config` first failed because a second CLI writer succeeded while an OS lock was held. The repaired merger refuses immediately with `busy`, preserves config bytes and succeeds after the first lock is released.
4. `LifecycleTests.test_codex_linked_ancestor_refuses_before_external_mutation` reproduced a refused configuration migration that nevertheless created an external `nested/hooks.json.install-lock` through a higher linked ancestor. Checking configuration ancestors before lock acquisition preserves the complete external file inventory.
5. `LifecycleTests.test_unrelated_template_status_basename_keeps_its_command` first failed because trusted-launch substring pinning rewrote a caller's `/user/scan-status.py` into a duplicate maintained launch. Exact supported historical command matching now preserves that caller command alongside the actual pinned status registration. No new broad restriction on caller templates or unrelated events is imposed.

Additional targeted public greens cover exact authentic old templates, all three providers' removed old-interpreter pinned commands, safe mixed-command refusal, missing status asset refusal and recovery, configuration hard-link byte/mode isolation, both real installers' upgrades of genuine old provider configurations and idempotence, and injected Gemini configuration-promotion failure followed by successful recovery. The existing Codex merge suite retains write-failure cleanup, preserved custom settings/group data, exact replacement launches, prior-interpreter replacement, unchanged-config refusal and malformed-template controls. Former expectations that mismatched owned pairs could be silently retained are replaced with the approved safe refusal contract, plus clearly user-owned same-basename preservation cases.

The existing installed scanner recovery tests remain explicit manual installed invocations after migration. Their fake-secret rejection, diagnostic recovery, startup/PATH isolation and Guardian controls are retained. Registration-drift diagnosis now alters an actually active Guardian registration. This is not a claim that the scanner remains automatically registered.

## Authentic offline migration fixtures

`scripts/fixtures/provider-hooks-pre-status/{codex,copilot,gemini}.json` retain exact template bytes from prepared base `0bf18e9764b9a2e00763e089af2c41a7710f6141`, before replacement. `provenance.json` records repository source paths, SHA-256, Git blob IDs and Git mode `100644`. The public tests consume these files without Git history. Existing T6/T7a release archives continue to cover only neutral runtime upgrade inputs; they did not contain provider templates. No present replacement template was used to synthesize a purported old release.

## Verification scope and environment

Observed environment: Python 3.14.6 and 3.13.14, PowerShell 7.6.7, RTK 0.51.0 at `/Users/adam/homebrew/bin/rtk`. Prefixed commands run normally; `rtk gain` could not open its tracking database under the sandbox. No raw command fallback was used. Disposable homes isolate provider/config/data/cache/profile roots and inherited `CODEX_HOME` according to the maintained lifecycle harness. Direct trusted Command Line Tools Git is available for repository gate checks.

Official standard-library contracts checked: [Python 3.13 msvcrt locking](https://docs.python.org/3.13/library/msvcrt.html#msvcrt.locking) documents immediate `LK_NBLCK` failure and current-position byte locking; [Python 3.13 fcntl flock](https://docs.python.org/3.13/library/fcntl.html#fcntl.flock) documents the POSIX lock. Native Windows code paths remain unexecuted here. PowerShell-on-macOS is installer parity proof, not NTFS/junction/ACL or native status-child containment acceptance. The adapter's existing native unavailable fallback remains unchanged; T8-W owns native positive delivery. The primary separately confirmed current Codex matcher mapping from [official Codex hooks](https://learn.chatgpt.com/docs/hooks); no matcher expansion or authenticated delivery claim follows.

The accepted neutral runtime build `82e125f8e74728baf01a0e1d792d4ec131f9a309d90b861b16287482dde9b029` and all 22 literal input hashes/modes were verified unchanged before and after the final serialized groups. The status renderer operational AST/SOURCE, all three generated status assets and Guardian source/assets remain unchanged from the accepted parent. The neutral build is recomputed as each ordered input basename, NUL and literal bytes. Scanner detector/policy, explicit repository gate and LFS behavior retain their prior accepted scope; this node adds the three public Git gate controls below, not a new complete LFS/capacity proof. I4 owns combined repair/turn-end acceptance; no unchanged capacity or performance proof is relabeled as T8b measurement.

## Exploratory failures and approval observations

Two auto-review rejections made no mutation. The first rejected a broad replacement of the Codex test file's `main` through EOF because it could delete or weaken existing regression coverage. Small targeted edits and additive public controls were used instead. The second rejected a proposal to constrain caller-provided templates to the desired registry because it could reject unrelated events/handlers and disrupt supported installation. That restriction was not resubmitted; ownership classification remains exact while supported caller-template compatibility is preserved.

An exploratory implementation batch had a Python quoting syntax error before any edits in that batch. It was corrected using simpler literal replacements. An existing settings-only Gemini installer fixture then exposed an accidental `template["hooks"]` lookup: supported templates without hooks now retain their original behavior through an empty-map default. macOS temporary paths also exposed the fixed system-alias distinction; user-created linked ancestors remain refused.

One exploratory orchestration loop started security-reporting while diagnostics still had a yielded process session. No generator or mutation overlapped them. Both drained successfully (diagnostics 10, reporting 14 in 73.841 seconds), but neither overlapping run is reused as frozen acceptance or timing evidence. The corrected final runner awaited actual process completion between every serialized group; its completed results below replace all exploratory acceptance/timing observations. The full Bash suite also passed an exploratory run, which is not reused below.

## Accepted prerequisite composition and final review controls

The primary's original SIGTERM reproduction against accepted T8a's Codex status asset (`92bbf7c68519d0495f46bd674df0ca2d99e105bba5ef50c081ac6858db9367f3`) returned `-15` and left its private status CLI child alive. The fresh bounded T8a-C owner `/root/repair_t8a_c` delivered accepted repair `3ff06db82a28764c0e67ee80a1e044886abc8fce`; it is present in exact parent `bb53a1370018475dd70d21e63e931e58215fed17`. The primary then returned exclusive ownership at clean provisional T8b tip `e3d1dee8a2334eac3323deb60506d095336888e8`. [T8b-M composition evidence](t8b-m-evidence.md) is immutable here, SHA-256 `5baa3bb4fdc75b5f6550baaad7083388cf6413f998256f98270a7e4bc499b33d`; it accepts only composition. [T8a-C evidence](t8a-c-evidence.md) retains its ordinary-signal delivery/cleanup scope and remaining SIGKILL/pre-handler/native limits.

After ownership returned, the two prepared public cases reproduced their distinct failures in one two-method run: plain `echo ~/.codex/hooks/load-required-skills.py` returned an ambiguous-ownership refusal, while duplicate Codex JSON keys returned success. The original Bash echo fixture remains intact. The repaired classifier preserves only literal output commands in known POSIX fields and retains refusal for substitutions, backticks, command sequences, pipelines, redirects and executable wrappers. Codex now refuses duplicate JSON keys without changing config bytes. The first focused four-method green took 0.279 seconds, and the refined omitted-event/strict-shell control pair passed in 0.584 seconds; these are focused observations, not final full-suite proof.

A further primary source candidate reproduced through the actual Copilot merger: `powershell: echo (python '/absolute/owned/scan-secrets.py')` with an unrelated bash command returned success rather than safe refusal. Literal-output proof is now restricted to known POSIX fields; PowerShell and `commandWindows` receive no POSIX exemption, and parentheses/braces are refused as evaluation syntax. A focused five-method group, including the positive original echo case and existing mixed-pair/override controls, passed in 0.448 seconds. This proves source migration inspection of PowerShell configuration on macOS, not native PowerShell host delivery.

Public FIFO configurations then reproduced hangs for all three providers, each terminated and waited by the test's one-second outer subprocess timeout. Both readers now admit only regular input files before reading bytes. A three-method green in 0.616 seconds covers prompt FIFO refusal, unchanged FIFO/backup identity, successful regular-config recovery and existing regular hard-link byte/mode isolation. A separate FIFO lock-path control already refused promptly on this POSIX host before any lock implementation change; no lock-path hang or native Windows result is claimed.

The pinned-old-interpreter fixture now explicitly removes `sessionEnd`/`SessionEnd` from caller replacement templates while positively executing the new `agentStop`/`AfterAgent` registered status action. This establishes retirement independent of template event membership. Existing authentic old fixture bytes are unchanged. The two obsolete module descriptions containing `Inactive` were updated under explicit authorization. The family renderer's operational AST/SOURCE and all three accepted generated status files remain byte-for-byte unchanged; only the six diagnostic build constants regenerate as canonical source identity changes.

## Final frozen receipt

All 26 groups passed serially with exit 0. The runner verified all 61 scoped input SHA-256/mode pairs before execution and after every group, ending with `FROZEN_INPUTS_UNCHANGED 61` and `ALL_GROUPS_PASSED 26`. The foreground process fully exited before final evidence or Git mutation. No functional test ran concurrently with another group or source/generator mutation in this final run.

Exact runner command: `rtk proxy python3 /tmp/t8b-final-runner.py`. Each group used a 900-second outer timeout without product-timeout changes or retries. For Python groups, `$PY` below is `/Users/adam/.pyenv/versions/3.14.6/bin/python3` or `/Users/adam/.pyenv/versions/3.13.14/bin/python3`. Each installer group used that version first in `PATH`, followed by `/Library/Developer/CommandLineTools/usr/bin`. Per-version disposable homes pinned `HOME`, `USERPROFILE`, `CODEX_HOME`, `APPDATA`, `LOCALAPPDATA` and all three XDG roots; global Git config was disabled. Installer/lifecycle tests additionally control their own disposable installed homes and remove source access for the relevant installed controls.

Final local logs/results: `/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/t8b-final-ha94zsmt`. `results.json` SHA-256 `1935f8c83fae1d08077dd939794314caaf4c7a37f44f73262ae8910697912df6`. Frozen input receipt `/tmp/t8b-final-inputs.json` SHA-256 `812209a343523d92305ac2ad49f835141dbb24a3b57e9f88714fccfdd8b91701`. Runner SHA-256 `ebe855fbb69bc9a06fdb2d91461680209c13bac405f0bed12944a76a39eb93c4`. The source/mode table below and per-group log fingerprints retain the reviewable receipt independently of old Git history.

| Group / exact command | Parsed test count per version | Python 3.14.6 outer seconds | Python 3.13.14 outer seconds |
| --- | ---: | ---: | ---: |
| `rtk proxy $PY scripts/generate-hooks.py --check` | script success | 0.243040 | 0.249217 |
| `rtk proxy $PY scripts/test-install-codex-hooks.py` | script success | 0.278580 | 0.219477 |
| `rtk proxy $PY scripts/test-scan-secrets-lifecycle.py` | 32 | 38.011944 | 36.715404 |
| `rtk proxy $PY scripts/test-scan-status-cancellation.py` | 5 | 1.842569 | 1.851385 |
| `rtk proxy $PY scripts/test-hook-diagnostic-recovery.py` | 17 | 65.038866 | 66.643392 |
| `rtk proxy $PY scripts/test-hook-diagnostics.py` | 10 | 2.133686 | 2.208421 |
| `rtk proxy $PY scripts/test-security-reporting.py` | 14 | 57.260731 | 57.626805 |
| `rtk proxy $PY scripts/test-generate-hooks.py` | 26 | 18.198515 | 17.575534 |
| `rtk proxy $PY scripts/test_test_all.py` | 14 | 10.650859 | 11.670868 |
| `rtk proxy bash scripts/test-install.sh` | script success | 83.685508 | 75.479521 |
| `rtk proxy pwsh -NoProfile -File scripts/test-install.ps1` | script success | 293.549314 | 283.061312 |
| `explicit-gate-controls (exact three-method command below)` | 3 | 8.718905 | 9.227186 |
| `rtk proxy $PY scripts/generate-hooks.py --check` | script success | 0.258911 | 0.233002 |

Exact gate control command:

```sh
rtk proxy "$PY" scripts/test-install-repo-gates.py \
  RepositoryPreviewTests.test_install_reinstall_commit_gate_and_uninstall_public_workflow \
  RepositoryPreviewTests.test_actual_push_rejects_intermediate_history_before_original_hook \
  RepositoryPreviewTests.test_source_free_neutral_install_activates_self_contained_real_git_gates
```

These controls exercise an actual installed commit rejection, actual push rejection for intermediate history before original-hook execution, and source-free installed real commit/push success. They retain the explicit repository owner-install boundary. The lifecycle groups each passed all 32 methods and timed 117 instrumented adapter callbacks: observed maxima 0.747269 seconds on Python 3.14.6 and 0.746940 seconds on Python 3.13.14. These are maxima over the instrumented calls, not every subprocess, p95, capacity or native-host measurements.

Both full PowerShell runs report the existing `Skipping: junction creation is not supported on this host.` and `test-install.ps1: all tests passed.` This is macOS PowerShell installer parity only; it does not establish native Windows filesystem/status containment acceptance. The user confirmed no local Windows environment exists. GitHub Actions execution is now authorized and primary-owned, but no hosted Windows result is included here. Authenticated Codex/Copilot/Gemini host delivery also remains separate. The two new FIFO lifecycle controls require POSIX `os.mkfifo`; full-file Windows execution requires appropriate fixture coverage and is not inferred from these passing macOS groups. This static fixture compatibility observation was sent to the primary for hosted-test composition; no frozen source was changed after the test window was released.

Post-run read-only checks passed: `rtk proxy bash -n scripts/install.sh scripts/test-install.sh`, PowerShell `Parser.ParseFile` for `scripts/install.ps1` and `scripts/test-install.ps1`, and `rtk proxy /Library/Developer/CommandLineTools/usr/bin/git diff --check`. A separate final read-only verifier rechecked all 61 file hashes/modes, all 26 log hashes, all 22 neutral inputs/build, immutable T8b-M receipt, unchanged generated status bytes and docstring-only status-family AST difference. No further functional/generator/installer suites were started after the primary released the exclusive window.

A transient user-question pause request arrived between groups. The controller's initial PID-selection assertion failed before any signal was sent; the serial runner naturally completed recovery/diagnostics and entered reporting while its state was inspected. The user resumed before any process was stopped. No test was killed, restarted, retried or omitted, and no frozen input changed. This does not reuse the earlier overlapping exploratory diagnostics/reporting observations.

### Frozen source/generated/test and protected input identities

All rows below were checked at every final group boundary. The mutable evidence file is intentionally outside this self-referential table; its final SHA is reported with the delivery commit. Modes are file permissions, matching the scoped freeze. T8b-M remains immutable. The accepted 22 neutral runtime inputs, three status outputs, cancellation suite/registry and Guardian inputs are included so composition can reuse their exact accepted identity.

| Path | Mode | SHA-256 |
| --- | --- | --- |
| `.codex/global-hooks.json` | `0o644` | `e36f7d84f3845ef20de8feb6a0c4bcc803bd93452baa0552e82237e69afa7a7e` |
| `.codex/hooks/helpers/tool_guard_policy.py` | `0o755` | `c3ee195c5bd9eb51c35c799f3d41cf39440d1ec7771917df5411aeecb07a60fe` |
| `.codex/hooks/hooks-diagnostics.py` | `0o755` | `ce2bae148c213c79de21ddeb45f1565a67f2a2597e4ac30006ccc2cafd95d3c6` |
| `.codex/hooks/scan-secrets.py` | `0o755` | `7528cece30be86579788aeda6c0d710509aa547426f3dbedba10cee9de10e8a5` |
| `.codex/hooks/scan-status.py` | `0o755` | `126de1936d82b294e15306d99ab1a35e312d9d55e239c5941d6266ef96cf84f3` |
| `.codex/hooks/tool-guard.py` | `0o755` | `fb9187e1236a7898b1cd3da0e7e2bac3699dd2fbbdc0c5b10d505ae8ced8158b` |
| `.copilot/hooks/hooks.json` | `0o644` | `e8228b9a31fa6813a1b94bef1f35e87e4ee8637e54c82e869f8085629cc4e5cc` |
| `.copilot/hooks/scripts/helpers/tool_guard_policy.py` | `0o755` | `c3ee195c5bd9eb51c35c799f3d41cf39440d1ec7771917df5411aeecb07a60fe` |
| `.copilot/hooks/scripts/hooks-diagnostics.py` | `0o755` | `1a5416ecf6edf001eaada40c093f8bcb335e7b29cc416c647f4df389c1190314` |
| `.copilot/hooks/scripts/scan-secrets.py` | `0o755` | `a8e1dcc8132b61067964851c82d8cfc5f3eae71886ef9dece64472de73ac1cdb` |
| `.copilot/hooks/scripts/scan-status.py` | `0o755` | `b85e4efd4d159746f0ff37b3c2800638a5d39173fa3031aa104e87f0677635da` |
| `.copilot/hooks/scripts/tool-guard.py` | `0o755` | `b72e015db17e1fe3333816aa3d6a8e11b42f68902ed05429fb83c558b504a6ef` |
| `.gemini/global-settings.json` | `0o644` | `73b93c66397830f961f999ba2b290b812415598c74a2db62ac94ac6072d53c44` |
| `.gemini/hooks/scripts/helpers/tool_guard_policy.py` | `0o755` | `c3ee195c5bd9eb51c35c799f3d41cf39440d1ec7771917df5411aeecb07a60fe` |
| `.gemini/hooks/scripts/hooks-diagnostics.py` | `0o755` | `c8cc09e9f3d27bcdeaedd29cae27f745623dc16884b2512b8e4e07f8eb68730d` |
| `.gemini/hooks/scripts/scan-secrets.py` | `0o755` | `e25defb542d2b118540c02cf81adb5f9050d4744d346e7f2f5f94aab18e76821` |
| `.gemini/hooks/scripts/scan-status.py` | `0o755` | `0fc85f1e234497eca04264bbaa0a7bf2008fe6c3c6cf26ad910558324fb16251` |
| `.gemini/hooks/scripts/tool-guard.py` | `0o755` | `de4fe77512c6b593b92efae3862f452dbaa98b5951f20113b159047124d27dfc` |
| `docs/hook-resilience-design-b/t8a-c-evidence.md` | `0o644` | `fb8035f7f9639641685b3973c87498da8fe56b39408303e62acba5ac2d59e5c5` |
| `docs/hook-resilience-design-b/t8b-m-evidence.md` | `0o644` | `5baa3bb4fdc75b5f6550baaad7083388cf6413f998256f98270a7e4bc499b33d` |
| `hooks/families/diagnostics.py` | `0o644` | `2d9177d738adec5ff4fab6f2a178171b7d21195aac70f7998433b72e51c3b668` |
| `hooks/families/scan_status.py` | `0o644` | `e466e15be05fd38b3110a3b08e92a9942d21963f08c0071e2f3be95ef4542c97` |
| `hooks/families/tool_guard.py` | `0o644` | `60cf773e2b40e62eba19ed5214e012156d71ab02401e5de54ea4ddd7f1021db7` |
| `hooks/registrations.py` | `0o644` | `6f6c2455c8be57e17a203cdffc134e8e9630609571674ae0bf7f4089f703b859` |
| `hooks/runtime/scan_allowlist.py` | `0o755` | `80eb5a115707ad03c227b6e3c1c43da463b0ce303a60909f398eab6dd9c7c7e7` |
| `hooks/runtime/scan_audit.py` | `0o755` | `86b5527ad96a9495079b4e3a5fdb6ed8562a900744665c39b9fdd9000ca18451` |
| `hooks/runtime/scan_budget.py` | `0o755` | `0ce123e105ef306fef10c7be66e1666ef890f55463b61360cd9c170fefd40ca0` |
| `hooks/runtime/scan_cli.py` | `0o755` | `b2000e9789fd44bb27bbf8dcc84d742af2bc5f11afdcbb5a2344aac11c12a1e1` |
| `hooks/runtime/scan_dispatch.py` | `0o755` | `99f5dcffe05e6b97f7fdac636154bfb9c65d03833963383ab6576236398dbe30` |
| `hooks/runtime/scan_engine.py` | `0o755` | `33bbfb091672a9ef5b03d04c291e9e91ec063945cbbfbc08a0007ab2c3ab2249` |
| `hooks/runtime/scan_gate.py` | `0o755` | `a8c36bcfad6aec72ac0ce9d9325a25cf9854eee7c9f15eda136251166b4381db` |
| `hooks/runtime/scan_git.py` | `0o755` | `36eae03a2429bf3a9bc6c6ed4913c1f882fbba72d1bd5b7ee64f0ab5660a57da` |
| `hooks/runtime/scan_lfs.py` | `0o755` | `bcd53cb7738e43f52e6097fbfeaf461b130f15b35f2912a7fba2d53b5aa6112b` |
| `hooks/runtime/scan_native_file.py` | `0o644` | `660222d89c1b01d3ef77a34920362c99d2567a11c98cdddc24db542e34a788fb` |
| `hooks/runtime/scan_private.py` | `0o755` | `3b910c861215f34cc69d1aa065a24a398d0e20fee39ee2a386be09d66b19a8e0` |
| `hooks/runtime/scan_publication.py` | `0o755` | `6e07c3ec4763671781963e4e12b237acf817e5f04f1a74376666ecbcebfe9bce` |
| `hooks/runtime/scan_repo_dispatch.py` | `0o755` | `6a21dd7ab4921e429031b956b2331b6af1db767ed16f54d41fb15c52c04f4078` |
| `hooks/runtime/scan_repo_install.py` | `0o755` | `fbf1021aaa0685b2e6581feea7c91e9466e0cc7dc2c6e1c1f30d689be096c0d3` |
| `hooks/runtime/scan_repo_state.py` | `0o755` | `69ea57e1af5a29eea6d1dbc2c950e14019bb3d7f90d5bdbe84bc62333dac402a` |
| `hooks/runtime/scan_reporting.py` | `0o755` | `c57d577217aed68e7e0e191c3225195a1950e0b4fd18c8524f93984a2de2d8c9` |
| `hooks/runtime/scan_repository.py` | `0o755` | `adfea4ca41a50ddd31d0fd15fb1b45c7ece29881a15321a84ece0fdc68b76775` |
| `hooks/runtime/scan_status.py` | `0o755` | `c70549592deb0db92ab44a6e5dac4352343f89afec903fc34647eff056d136fc` |
| `hooks/runtime/scan_stream.py` | `0o755` | `2b91062b6440457ca26488d9dba43e2a4bda9d2a7dc309e256da1c0b6c9b707b` |
| `hooks/runtime/scan_transaction.py` | `0o755` | `005b2bb173cadf708ccc0f1041404c90797421843a8a88d07e2c626497c90894` |
| `hooks/runtime/scan_types.py` | `0o755` | `57f6116d711302a3c106556caa4f6ed98aa60a7b2e5a8f6cd78081b914e6581e` |
| `scripts/fixtures/provider-hooks-pre-status/codex.json` | `0o644` | `15d1f58f3c245e1cc514b1e3e0992d131cdac249f55f59ace10b5750ef17bb08` |
| `scripts/fixtures/provider-hooks-pre-status/copilot.json` | `0o644` | `a05b4871cdf151486f1f2e4a2a4f2e05bbefb580cf43dc4649529ef54a11ccac` |
| `scripts/fixtures/provider-hooks-pre-status/gemini.json` | `0o644` | `6686efb4dc6477391c0ae2347ca87618efff1843553c252ada102da3d0bf221e` |
| `scripts/fixtures/provider-hooks-pre-status/provenance.json` | `0o644` | `e08bd1bbe5fdb399997b9487d94496935b977d144928bb65ee656e78d57e820b` |
| `scripts/install-codex-hooks.py` | `0o755` | `ab896fad81b3206412ab76dcabeb8b0637692b1a27d110de17a4c5d6868a17ab` |
| `scripts/install-provider-hooks.py` | `0o755` | `554ad7a9bcdd7ea5a006235d9170ea464f16d596fbf33e9cc2eaf4379714aad4` |
| `scripts/scan-secrets.py` | `0o755` | `ea9f6adf225889e0ff9297d32e88e9660cea6a9d917ca87f6d95ada6d3afc497` |
| `scripts/test-all.py` | `0o755` | `c5c534c9e9430c0a06eb34c5519b5718008fff82526dc5b95c3f617603bad79a` |
| `scripts/test-hook-diagnostic-recovery.py` | `0o755` | `34d66f12c2d617197414a9e5d4267e88709c45d8a4f75b9b3e2e6ddfae3c3c37` |
| `scripts/test-install-codex-hooks.py` | `0o755` | `11b40db0e40f2cbca532c189294d44780a6b04b54e5fac0878669acb8ab1465d` |
| `scripts/test-install.ps1` | `0o755` | `3870d09a1760b7923f5833faed4f7d33ed8dda555650eeaa1b3565b90ca71567` |
| `scripts/test-install.sh` | `0o755` | `240d54a97cfaf93dedf8437dc2a8986e155b1f8d007fbeff4107abd2f9830cf6` |
| `scripts/test-scan-secrets-lifecycle.py` | `0o755` | `57a9cb8b6c7d6a987d2ba5891e6e41256b1bfd934cc495aa127adf38ae33f2a6` |
| `scripts/test-scan-status-cancellation.py` | `0o755` | `1a3853d0a248ca6bb4d0a50124a7623737cf3c78284fc5c00ccc2f8c191b455d` |
| `scripts/test_test_all.py` | `0o644` | `711f44c44bda33e88324a3b8c5acaeaa7f5f84721fd320b394d2f5a36c939b71` |
| `scripts/trusted_hook_launch.py` | `0o644` | `74be015faa4ab45eb5aa8135bb170657faae3ae47fa29707952d83fbf1e5df37` |

Canonical diagnostic build identities (the six generated scanner/doctor files, not neutral runtime build identities):

| Provider | DIAG_BUILD |
| --- | --- |
| Codex | `a83dbfa1abf25de308382d480740c3ce9a04d1db976379ed23a4864b0571c2e5` |
| Copilot | `82589548103a2b61300286e6bd75cc663feee86a922297bab6b9bbe0a6330b82` |
| Gemini | `0f4fd663cba3257cd647d5bc392826f72ed1784867159c54bde82b03ca64d349` |

### Final log identities

| Group | Python 3.14.6 log SHA-256 | Python 3.13.14 log SHA-256 |
| --- | --- | --- |
| `freshness-before` | `2fc777477107273d19ce3de6623e17beb28db17ff20c1464e68f23f411d2d1c9` | `2fc777477107273d19ce3de6623e17beb28db17ff20c1464e68f23f411d2d1c9` |
| `codex-merger` | `ff82e9fd545fdfee493050ca7880a50479af902005799dfa445758bec37d2318` | `ff82e9fd545fdfee493050ca7880a50479af902005799dfa445758bec37d2318` |
| `lifecycle` | `a6073b43b0349a74cd19e8b63f644ead04092d957bc6c15543459a823bf1c6a7` | `d69d192ae6961681e2f83baf1deb9bd5051def374f954e9061621e5113b15728` |
| `cancellation` | `b12a86069f0e6a611805d477983c70cb439e0f24f24ffecf172959e0da1cdc72` | `0d6ad159192f1a8c4e6644bb49e356aead8727b8a05104e34ae88d0bf84141f4` |
| `recovery` | `052f14436bb1ed5762ae4aa0299875fe27faf4bed4f217a62c969f0862cd7186` | `6260a8a6a16362517a234ea8e36e04d8c9ee0efb10a4cb62ff3c75e7ad68e8af` |
| `diagnostics` | `ee11015fa713077f98f1613ebe3f271a8b0bf10eddf97c85953b7b57ffcad70d` | `a4b50024ab5a16b1bc70f986a22fab3e433cd4de77e54aed1aaca0f34a343f8e` |
| `reporting` | `a583f8d3a06050b9a34e5e7f280a16d3c892f8908cc94047cbefbb669fcb40b3` | `611256f182e2217ed02b32648bf9769fe744fed37402d6d3a7df597601864db9` |
| `generator` | `3e0ce080d2931559d2859715352af453b0d08d56e53cb99c107d83f06705afe1` | `090f9b034e5110d08bf9ce37119268459323f9322faf3894b732ed517c7c5901` |
| `runner` | `ac556a011f8bca74618af430cc793bcc46dc7312d27102be9dc4ed6f667274df` | `c51a0c14a826323fde12aaae76bd1085d32dbae70f829c09ced77eb1ad3c0ffe` |
| `bash-installer` | `629915b97170602e6d3dfa6ae9f1f49d484f13355e88d9075350b3857a76bc44` | `32a4eee43d18956a33e85e3649b3efc207557dab9670e5249a2ba1459c058b10` |
| `powershell-installer` | `322943b747d8ebaed90a9ba0d376e681f45ac63cc381af2fe7a103e1d070b803` | `322943b747d8ebaed90a9ba0d376e681f45ac63cc381af2fe7a103e1d070b803` |
| `explicit-gate-controls` | `4c5199b11efbc064304071664786d9dd50d228fd4a7cac02faba15e5ca51dc6e` | `aba51646ac44787c694ed581e43958e9d8583dec5175478b43014b13a2629823` |
| `freshness-after` | `2fc777477107273d19ce3de6623e17beb28db17ff20c1464e68f23f411d2d1c9` | `2fc777477107273d19ce3de6623e17beb28db17ff20c1464e68f23f411d2d1c9` |

T8b stops at this migration and local proof. Primary review/integration, coordinated KB maintenance, I4 combined acceptance and native/authenticated delivery remain separately owned. No branch push, PR, deployment, real-home install or owner trust/enablement mutation was performed by this node.
