# T8a: inactive status assets and documented diagnostic metadata

Date: 2026-10-16. Branch: `codex/design-b-t8a`. Base: `280b72c8`. Prerequisite: accepted I3-P `cf85ee4c32866844d27dfa3a82d88796dfd34f9c`, following neutral upgrade repair `76619bd6012231f677fb946aa4893788b8c15608`.

## Delivered boundary

T8a supplies generated, inactive `scan-status.py` assets for Codex, Copilot and Gemini, and narrowly admits documented Codex outer metadata for the exact diagnostic recovery request. Active templates and both registration mergers remain byte-identical to the prerequisite. T8b owns activation, exact retirement and positive installed registration migration. The primary owns the plan, final integration and coordinated KB pass.

The adapter has no provider scanner-helper dependency. Its POSIX child uses the current isolated, pinned Python interpreter and the fixed default neutral bundle entry at `~/.local/lib/scan-secrets/scripts/scan-secrets.py`. The only neutral action is `status --json --no-input --repo PATH`. A validated absolute native `cwd` selects the worktree; absent `cwd` uses process cwd, while invalid `cwd` returns unavailable. There is no PATH executable lookup, environment command override, Git invocation, detector/SQLite startup, content/index scan, checkpoint, retry, watcher or background task.

Input is capped at 65,536 bytes and 0.12 seconds. A complete JSON object can finish with stdin still open; duplicate keys, trailing input, invalid UTF-8, incomplete/open input or larger envelopes return unavailable. Stop envelopes can contain a large `last_assistant_message`; exceeding these limits is deliberately nonblocking and never triggers a retry. The child deadline is 0.70 seconds from adapter startup, including input time, with 0.10 seconds reserved for cleanup. A separate isolated Python bridge sets `RLIMIT_FSIZE` to at most 65,536 bytes, then `execv`s the exact neutral entry in the same private process group. The adapter caps captured output, discards stderr, kills the private group even after root exit, and reaps the root before its final response. [Python's documented fork-gap warning](https://docs.python.org/3.14/library/subprocess.html#popen-constructor) motivated removal of `preexec_fn`; this was an API robustness finding, not a reproduced deadlock. Ordinary local process/filesystem behavior is covered; uninterruptible kernel operations and process-creation stalls are not a hard real-time OS guarantee.

Saved clean/findings/incomplete outcomes display only fixed result/scope labels and a bounded timestamp, always marked historical and never authorizing publication. Absent, corrupt, unreadable, malformed, failed, missing or timed-out status produces successful unavailable/not-scanned output. Repeated callbacks ignore `stop_hook_active` for enforcement. Codex/Gemini and VS Code Stop emit one `systemMessage` JSON result. Identified Copilot CLI input emits one display-only progress JSON line before one final `{}`. Unknown or malformed Copilot input uses one portable final JSON document. No response contains deny/block/continuation, or instructs an automatic checkpoint. A closed stdout consumer finishes quietly after cleanup.

Native Windows deliberately returns unavailable without reading input or starting an uncontained status child. The manual status interface is retained, but native Windows child containment, native delivery and associated preparation/proof remain open for the Windows follow-up, T9c and V1. PowerShell running on macOS is installer parity evidence only. No authenticated provider host delivery, live-home installation, trust/enablement change or external publication occurred.

## Metadata admission

`hooks/families/scan_secrets.py:_RECOVERY_SOURCE` admits Codex `model` and `turn_id` strings (at most 256 characters), `transcript_path` as null or a string of at most 8,192 characters, and `permission_mode` exactly in `default`, `acceptEdits`, `plan`, `dontAsk`, `bypassPermissions`. Other existing metadata bounds remain intact. This follows the primary's 2026-10-16 verification of [official Codex hooks](https://learn.chatgpt.com/docs/hooks). Copilot framing follows the saved [raw reference](../../.agents/sources/copilot-hooks-ref.md) and [official reference](https://docs.github.com/en/copilot/reference/hooks-reference); [VS Code](https://code.visualstudio.com/docs/agents/reference/hooks-reference) and [Gemini](https://geminicli.com/docs/hooks/reference/) remain distinct surfaces.

The executable diagnostic request remains exactly `cmd=hooks-diagnostics-v1`, `login=False`, with optional exact integers `max_output_tokens` and `yield_time_ms` in the existing range. Unknown executable fields, changed command/login, booleans masquerading as integers, invalid metadata and malformed arguments retain the ordinary strict route. Tool Guardian's canonical policy source is unchanged, and public clean/unsafe controls still pass with the newly admitted metadata.

## Public failing observations and repairs

- Exact Codex diagnostic plus documented metadata initially returned a normal scanner denial with `git_unavailable`, instead of diagnostic recovery: one failing method, 0.066 seconds. The focused metadata test passed after the canonical repair (0.580 seconds), and remains in the full recovery suite.
- The first source lifecycle test failed all nine provider/repeated-callback subcases because the proposed assets did not exist (0.080 seconds). After generation, the method passed (0.304 seconds).
- A complete disposable real Bash installation exited successfully but omitted `~/.codex/hooks/scan-status.py`: the installed public test raised `FileNotFoundError` (0.921 seconds). Both installers' exact Codex copy/preflight lists and matching asset assertions now include it. Copilot/Gemini remain independent bulk-copied provider-local assets.
- A real linked worktree with findings, while process cwd held a clean saved result, displayed the wrong clean history: one failure, 0.738 seconds. Explicit validated native cwd selection repairs it, with invalid cwd returning unavailable.
- Parsing malformed Copilot output as one VS Code-compatible final JSON document initially raised `JSONDecodeError: Extra data` (0.037 seconds). Unknown/error envelopes now emit one final document; identified CLI envelopes retain documented progress framing.
- Closing the status output consumer while a known child hung initially returned exit 120 and `BrokenPipeError` during interpreter flush (0.831 seconds). Explicit flush, error handling and stdout redirection now finish successfully and quietly after cleanup.

Fixture setup initially exposed required source-directory omissions; those were corrected before the successful-install/missing-asset reproduction. The generator's two exact count assertions initially expected 62 assets; both failed against the correct new inventory of 65 (26 methods, 17.173 seconds), and now truthfully require 65. An initial sandboxed cleanup probe produced six `PermissionError` errors for `/bin/ps` (6 lifecycle methods, 9.835 seconds); authorized process inspection reruns preserve the same cleanup assertions and pass. No failing test was removed, disabled, skipped or weakened.

## Final verification

All following groups ran serially against the frozen source. The lifecycle suite uses real standalone processes, actual Git linked-worktree flows and real installers in disposable homes. Both main installer fixtures remove their entire disposable source checkout, verify all three installed asset bytes and the selected interpreter receipt, then execute installed adapters with scanner helper faults. All lifecycle states and error paths return nonblocking native results; hostile PATH/PYTHONPATH/CLI overrides and scanner/Git startup sentinels remain untouched. Recovery's generated-process controls retain ordinary permit decisions and Guardian's protected-operation denials; actual host tool dispatch remains separate I4/V1 evidence.

Commands below ran from `/Users/adam/.codex/worktrees/design-b-t8a/skills`, prefixed with `rtk proxy`. Python suite commands used the explicit `/Users/adam/.pyenv/versions/{3.14.6,3.13.14}/bin/python3` interpreter; installer environments put that interpreter directory first on PATH. Observed tool versions: RTK 0.51.0, Python 3.14.6/3.13.14, Git 2.54.0 (Apple Git-157), PowerShell 7.6.7. Suite elapsed times are subprocess wall times, not authenticated provider delivery or a production performance benchmark.

The temporary orchestration runner interrupted the first full macOS PowerShell installer attempt at an external 240-second allowance. No suite assertion failure was observed, and process inspection found no abandoned validation descendants. Only that incomplete group was rerun with a 900-second outer runner allowance; it completed in 280.617 seconds. No product deadline or suite assertion changed. The retained final PowerShell logs report the existing unsupported-host junction-creation skip, so this result does not prove NTFS/junction behavior or native Windows support.

| Command (Python prefix where applicable) | Result | 3.14.6 environment seconds | 3.13.14 environment seconds |
| --- | --- | ---: | ---: |
| `scripts/generate-hooks.py --check` | 65 assets current | 0.242 | 0.262 |
| `scripts/test-scan-secrets-lifecycle.py` | 13 methods, previous test shape | 19.678 | 18.879 |
| `scripts/test-generate-hooks.py` | 26 methods | 18.402 | 17.260 |
| `scripts/test-hook-diagnostic-recovery.py` | 17 methods | 66.455 | 64.339 |
| `scripts/test-hook-diagnostics.py` | 10 methods | 2.082 | 2.167 |
| `scripts/test-security-reporting.py` | 14 methods | 71.067 | 70.569 |
| `scripts/test-install-codex-hooks.py` | public merge PASS | 0.275 | 0.205 |
| `scripts/test_test_all.py` | 14 methods | 10.645 | 13.049 |
| `bash -n scripts/install.sh` | syntax exit 0 | 0.007 | 0.012 |
| `bash scripts/test-install.sh` | full suite exit 0 | 82.419 | 76.629 |
| `pwsh -NoProfile -File scripts/test-install.ps1` | all tests passed; host junction limit | 280.617 | 281.658 |

The Python 3.14 full lifecycle observation measured a maximum of 0.745681 seconds across 108 callbacks; Python 3.13 measured 0.751000 seconds across 108. These 13-method full runs used lifecycle test SHA-256 `b4d73c99467bcc4d4e25cf48b4e98d37e4e2b94a03aba1b30f4cf33c9180ddcc`. The final file has 14 methods after the narrowly reviewed harness correction below; a full 14-method run is not claimed. The product renderer/generated/runtime bytes stayed frozen throughout.

A final harness review found inherited `CODEX_HOME` was not overridden, although current-environment inspection confirmed it was unset during the completed full runs. A public subprocess control then gave each real installer fixture its own disposable inherited `CODEX_HOME` trap. Both independent traps gained `agents/fixture.toml` and the installer ownership manifest: two failing subcases in 4.822 seconds. The sole environment repair pins `CODEX_HOME` to `self.home/.codex`. Inspection confirmed `HOME`, `USERPROFILE`, `XDG_DATA_HOME`, `LOCALAPPDATA` were already pinned in setup, and `XDG_CONFIG_HOME`, `XDG_CACHE_HOME`, `APPDATA` were already pinned for the main installer subprocess. An initial shared-trap control also failed in 4.836 seconds; independent traps replaced that shared fixture state before the definitive red.

Against the final 14-method file, run the three affected public methods:

```text
rtk proxy /Users/adam/.pyenv/versions/3.14.6/bin/python3 scripts/test-scan-secrets-lifecycle.py LifecycleTests.test_bash_installed_source_free_assets LifecycleTests.test_powershell_installed_source_free_assets LifecycleTests.test_inherited_codex_home_stays_untouched
rtk proxy /Users/adam/.pyenv/versions/3.13.14/bin/python3 scripts/test-scan-secrets-lifecycle.py LifecycleTests.test_bash_installed_source_free_assets LifecycleTests.test_powershell_installed_source_free_assets LifecycleTests.test_inherited_codex_home_stays_untouched
```

Observed: three methods pass in 9.549 seconds on Python 3.14 and 8.917 seconds on Python 3.13. The selected direct installer callbacks measured at most 0.064900 and 0.055346 seconds respectively across six callbacks per run. Both independent inherited traps stay untouched. These focused reruns are not a full 14-method pass. Earlier unchanged-method observations retain their stated previous-test-shape scope. The primary reviewed the production implementation and this narrow harness repair across correctness, readability, architecture, security and performance, with no unresolved findings.

All Python groups select explicit interpreter binaries. For both Bash/PowerShell full suites, the outer runner prepends the selected interpreter's `bin` directory to discovery PATH. The lifecycle setup does the same for its direct installer fixtures and additionally asserts the neutral `installation.json` interpreter equals the resolved selected `sys.executable`. The full installer environment selection and the directly asserted source-free interpreter receipts are distinct evidence. Full run logs and orchestration receipts are retained at `/tmp/t8a-validation-results.json` and `/tmp/t8a-<version>-<suite>.log` for the coordinating review; durable commands, results and limitations are retained here.

## Frozen runtime and generated identities

The neutral runtime build remains `82e125f8e74728baf01a0e1d792d4ec131f9a309d90b861b16287482dde9b029`. All 22 literal build inputs independently match `280b72c8`; no checkpoint, gate, LFS, installation-state or capacity policy changed. The primary independently confirmed this build and 31 unchanged runtime/entry/neutral-installer/active-template/merger/trusted-launch/Guardian files. Reuse the separately scoped seven final source/source-free installed groups, six ordinary capacities and seven phase/RSS groups in [accepted I3-P evidence](i3-p-evidence.md); none was redundantly rerun or relabeled here.

The generated legacy scanner reporting build is `90cc895f0e9735fe`; Guardian reporting build is `ebaa2bd0a1f1b4ef`. Their canonical policy sources are unchanged except the narrowly documented scanner diagnostic recovery admission; generated build identities reflect the new canonical family/inventory. Provider diagnostic build IDs:

| Provider | Diagnostic build |
| --- | --- |
| Codex | `b0d76a439d428be379f956d51238e408d3a2d48b6ee409201af3f83f0bf9f6f3` |
| Copilot | `8db3571ba644c56b12d2a5c0c177c890cfdb4b94683068a65a47a1a0a8681781` |
| Gemini | `f194a28b822b6bbf2edd5a474ae1ed98345c571f86fe83d29267f2e91628884d` |

The primary's original 25-file SHA-256/mode receipt matched the frozen tree. Only the lifecycle test changes afterward for the explicitly documented harness repair. Current task source/test/generated fingerprints follow; the evidence file itself has a separately reported final digest to avoid a self-referential checksum.

| Task file | SHA-256 | Mode |
| --- | --- | --- |
| `.codex/hooks/hooks-diagnostics.py` | `9bb50ee72e3d37d4e5077b9fbc72b0638a9a0a6bb8488fe972bbfddee0f26f15` | `0o755` |
| `.codex/hooks/scan-secrets.py` | `358bf3caec239c6156a2a94671975db7b81ba459c52a6c7855b5788969b7f6e3` | `0o755` |
| `.codex/hooks/scan-status.py` | `92bbf7c68519d0495f46bd674df0ca2d99e105bba5ef50c081ac6858db9367f3` | `0o755` |
| `.codex/hooks/tool-guard.py` | `fb9187e1236a7898b1cd3da0e7e2bac3699dd2fbbdc0c5b10d505ae8ced8158b` | `0o755` |
| `.copilot/hooks/scripts/hooks-diagnostics.py` | `6d2343bf0ca234c310b4bb656b011011e612c8d294663e16fba7e3a0944b2d7f` | `0o755` |
| `.copilot/hooks/scripts/scan-secrets.py` | `7dece6d6ff59fe737c7cf2b99266736dbd6b0a42c807733e2b8df31539328503` | `0o755` |
| `.copilot/hooks/scripts/scan-status.py` | `5d6f2cb55632c46a18d0452bc746391074b7669d4df2bfb20746ee4474933ae4` | `0o755` |
| `.copilot/hooks/scripts/tool-guard.py` | `b72e015db17e1fe3333816aa3d6a8e11b42f68902ed05429fb83c558b504a6ef` | `0o755` |
| `.gemini/hooks/scripts/hooks-diagnostics.py` | `2990937074eec0d20481a19ba20e735672a5ba6312c157fc6d9fd193d046419f` | `0o755` |
| `.gemini/hooks/scripts/scan-secrets.py` | `536135e2fb911fc1373403c97fd52dcdf8c10aacbb9f542e33b89eb139fedaa3` | `0o755` |
| `.gemini/hooks/scripts/scan-status.py` | `1222c40d0ff8b884195a6a25bf7f1fea825ca16f5e5bba6ec859886e65bf35b9` | `0o755` |
| `.gemini/hooks/scripts/tool-guard.py` | `de4fe77512c6b593b92efae3862f452dbaa98b5951f20113b159047124d27dfc` | `0o755` |
| `hooks/families/diagnostics.py` | `6662ca7fb81310acad4e5d53f23687a7e770677439a510952511c3b46bc0ae81` | `0o644` |
| `hooks/families/scan_secrets.py` | `77027b67a4cc7599efd6ec21fadc7516eb5042a1c66650fe6b56df2859dcabca` | `0o644` |
| `hooks/families/scan_status.py` | `bbfaa874ae4ada710300387376325fbe352a9cf87493656fb6229c83ecabeb5b` | `0o644` |
| `hooks/manifest.py` | `9cbba46f5d2822761d110d747b1adde29a7465ce51b89dbb3eb43fd6a5792ef1` | `0o644` |
| `scripts/install.ps1` | `664486797aff7148c4892aae479591e9b2c520845881101eaf3f5a2fada45174` | `0o755` |
| `scripts/install.sh` | `8215053b70a2e93a0594fb408b5fd89105141010b7cbcb1444325e9dab65cf89` | `0o755` |
| `scripts/test-all.py` | `b6de20d2bd276a2a8d1978e11d4489b6769fe7ff711c532c6fc1f2644f56badf` | `0o755` |
| `scripts/test-generate-hooks.py` | `3cb2993ca69efb56f58d865852702917e01baeb6ab5dae71beaaaff24f3ba4c6` | `0o755` |
| `scripts/test-hook-diagnostic-recovery.py` | `e9779f5f6d7e0564d320a998c6a1b40ffc66d3cb06b900519b5914e7774bcb21` | `0o755` |
| `scripts/test-install.ps1` | `3ddb2424a8b36f01343cb1b22da6772d487f97fade7de584eda9208da9182f97` | `0o755` |
| `scripts/test-install.sh` | `f98f8d9891103f57c09bce0f7a4c5c8d02afb853498cccd06a0f959ae7409f26` | `0o755` |
| `scripts/test-scan-secrets-lifecycle.py` | `a889bb89ce85fc4156f316d45f512ed71d36b9cedf52389f48984f917eafd852` | `0o755` |
| `scripts/test_test_all.py` | `db6b176016e1ae10b14cc7b62d37633c5b9989778b87c6f36800a1861316ff00` | `0o644` |

The 22 unchanged neutral build input fingerprints:

| Runtime input | SHA-256 |
| --- | --- |
| `scripts/scan-secrets.py` | `ea9f6adf225889e0ff9297d32e88e9660cea6a9d917ca87f6d95ada6d3afc497` |
| `hooks/runtime/scan_cli.py` | `b2000e9789fd44bb27bbf8dcc84d742af2bc5f11afdcbb5a2344aac11c12a1e1` |
| `hooks/runtime/scan_status.py` | `c70549592deb0db92ab44a6e5dac4352343f89afec903fc34647eff056d136fc` |
| `hooks/runtime/scan_types.py` | `57f6116d711302a3c106556caa4f6ed98aa60a7b2e5a8f6cd78081b914e6581e` |
| `hooks/runtime/scan_reporting.py` | `c57d577217aed68e7e0e191c3225195a1950e0b4fd18c8524f93984a2de2d8c9` |
| `hooks/runtime/scan_allowlist.py` | `80eb5a115707ad03c227b6e3c1c43da463b0ce303a60909f398eab6dd9c7c7e7` |
| `hooks/runtime/scan_stream.py` | `2b91062b6440457ca26488d9dba43e2a4bda9d2a7dc309e256da1c0b6c9b707b` |
| `hooks/runtime/scan_git.py` | `36eae03a2429bf3a9bc6c6ed4913c1f882fbba72d1bd5b7ee64f0ab5660a57da` |
| `hooks/runtime/scan_engine.py` | `33bbfb091672a9ef5b03d04c291e9e91ec063945cbbfbc08a0007ab2c3ab2249` |
| `hooks/runtime/scan_native_file.py` | `660222d89c1b01d3ef77a34920362c99d2567a11c98cdddc24db542e34a788fb` |
| `hooks/runtime/scan_audit.py` | `86b5527ad96a9495079b4e3a5fdb6ed8562a900744665c39b9fdd9000ca18451` |
| `hooks/runtime/scan_budget.py` | `0ce123e105ef306fef10c7be66e1666ef890f55463b61360cd9c170fefd40ca0` |
| `hooks/runtime/scan_repository.py` | `adfea4ca41a50ddd31d0fd15fb1b45c7ece29881a15321a84ece0fdc68b76775` |
| `hooks/runtime/scan_gate.py` | `a8c36bcfad6aec72ac0ce9d9325a25cf9854eee7c9f15eda136251166b4381db` |
| `hooks/runtime/scan_transaction.py` | `005b2bb173cadf708ccc0f1041404c90797421843a8a88d07e2c626497c90894` |
| `hooks/runtime/scan_lfs.py` | `bcd53cb7738e43f52e6097fbfeaf461b130f15b35f2912a7fba2d53b5aa6112b` |
| `hooks/runtime/scan_private.py` | `3b910c861215f34cc69d1aa065a24a398d0e20fee39ee2a386be09d66b19a8e0` |
| `hooks/runtime/scan_publication.py` | `6e07c3ec4763671781963e4e12b237acf817e5f04f1a74376666ecbcebfe9bce` |
| `hooks/runtime/scan_dispatch.py` | `99f5dcffe05e6b97f7fdac636154bfb9c65d03833963383ab6576236398dbe30` |
| `hooks/runtime/scan_repo_install.py` | `fbf1021aaa0685b2e6581feea7c91e9466e0cc7dc2c6e1c1f30d689be096c0d3` |
| `hooks/runtime/scan_repo_state.py` | `69ea57e1af5a29eea6d1dbc2c950e14019bb3d7f90d5bdbe84bc62333dac402a` |
| `hooks/runtime/scan_repo_dispatch.py` | `6a21dd7ab4921e429031b956b2331b6af1db767ed16f54d41fb15c52c04f4078` |

## Remaining owner actions

T8a is inactive asset/schema delivery with POSIX source and disposable source-free installed proof. T8b must activate exact pinned status registrations, reconcile exact historical scanner ownership and preserve unrelated settings/handlers. In particular, extend trusted launch/maintained registration ownership only when activating the new status handler; those merger changes were intentionally not made here. Keep independent stop validators intact. Native Windows containment, actual native behavior, authenticated provider visibility, combined lifecycle integration and production deployment remain open in the active plan. The primary owns plan/README/CI/KB reconciliation and the single coordinated end-of-session `update-agent-docs` pass; this delegated node did not run that pass or change those owner files.
