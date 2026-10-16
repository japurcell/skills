# T7b-P POSIX repository activation and recovery evidence

This scoped worker evidence belongs to `codex/design-b-t7b-p`, based on `560c33cc739f26bb74f5e1e1245c5e360a68f203`. The primary owns integration, the ExecPlan, shared source maps, registry/CI policy and the coordinated knowledge-maintenance pass. No deployment, real-home installation, external push, PR, native Windows delivery or production-capacity acceptance is claimed.

## Delivered behavior

The authoritative `scan-secrets hooks install/uninstall` CLI now performs explicit POSIX activation/restoration, while `--dry-run` remains read-only. The existing thin helper continues forwarding to that one parser. Installation probes the exact Python >=3.12 SQLite capabilities before mutation, selects a trusted direct Git (Apple launchers require explicit selection), preserves legitimate global/system configuration inputs, and never runs hooks, managers, credential helpers or network during discovery/preparation.

Complete private generations live under `.git/scan-secrets/installations/<generation>`. Each contains the exact neutral runtime, original-hook records, 28 supported hook launchers, exact T6 publication bindings and private configuration backups. A separate root phase journal identifies the selected generation. Reinstall is a semantic no-op when unchanged; explicit changed destination/runtime/budget-location/data selections or admitted original-hook edits prepare another complete generation. Uninstall retains generations/backups and preserves unrelated current settings and original hook edits. An originally absent `config.worktree` is restored to absence.

Installer `flock` plus the applicable Git `config.lock` serialize cooperating writers. Configuration is captured/rechecked while held. Prepared/active/retiring/retired journals support explicit recovery using exact full lock identity; changed or foreign lock files are preserved. This is not atomic compare-and-swap against an editor directly replacing configuration during final promotion. Unjournaled orphan preparation, ambiguous locks, partially changed locks and changed/unknown owned content require review; recovery never guesses ownership or deletes such content.

Preparation writes use held directory descriptors. Git edits only a private configuration copy through an isolated pinned-Python child bridge that `fchdir`s to a passed directory descriptor, closes it and `execve`s the selected Git in the same process group. This avoids pathname substitution without parent cwd changes, a second config parser, `preexec_fn`, or a persistent process. Ordinary/default/native capture paths remain unchanged.

Original hooks run at their ORIGINAL paths with original arguments, cwd, streams, sibling-resource resolution and exit status. The 26 unrelated launchers are self-contained stdlib-only passthroughs, so missing scanner helpers cannot prevent checkout/repair through reference-transaction or post-index-change. Commit/push gates retain exact ownership/build/original-hook validation. An explicit install recaptures safe original additions/edits; healthy-source uninstall can remove our binding despite changed original hooks or missing gate helpers, but preserves and refuses changed or unknown owned bytes.

Pre-commit privately captures the current trusted owner-only budget file, captures Git's actual selected index, validates the separate scanner result against caller-owned identities and reconciles parent/child capture/temp resources before admission. Partial and alternate-index actual commits preserve Git's selected content. Pre-push reuses T6's exact schema-1 binding and private verified uploader, adds no upload to inspection-only gate, forwards the pinned direct Git to the scanner child, and displays bounded validated finding locations/rules on rejection. Original hook PATH is preserved, including Git's own PATH prefix.

Ordinary repositories and explicitly selected ALREADY ENABLED worktree scope are supported. Existing sibling worktrees without per-worktree scope, included local hooksPath bindings, branch-dependent includes, URL rewrites and unsupported managers/custom LFS arrangements are refused instead of broadening coverage. Stable inherited/global includes and relative hook paths are supported; global/shared hook directories and remotes are never modified. LFS keeps the accepted macOS/SHA-1/local ordinary storage/Git LFS 3.8.0/basic-HTTP boundary. HTTP is loopback-only. Non-LFS SHA-256 support remains distinct. Native Windows activation remains explicit safe refusal and a separate task.

Discovery retains 10-second/2-second command/64-KiB file/1-MiB capture/2048-setting/128-worktree limits. Installation uses a separate finite 20-second/1-MiB runtime-file/16-MiB capture+temporary/128-owned-file/16-generation envelope; an owner-selected LFS tool is streamed within 64 MiB. Ownership uses the SAME 65536-byte bound before promotion and in healthy/runtime readers. Neutral packaging remains exactly 64 maximum inventory entries / 58 maximum assets; two added normal modules reduce synthetic extras, without raising those bounds.

## Actual red/green observations

- Null/list/integer `installed_value` in a private repository manifest initially returned exit 2 `internal_error`. Strict schema/type admission now returns exit 3 `installation_ownership_invalid`, preserves bytes and gives review guidance. The primary independently reran the null-value CLI case and confirmed identical fixture fingerprints at the final build.
- Touching an admitted actual Git copy at the same selected path initially made explicit reinstall report an unchanged no-op. Reinstall now captures its current exact identity; a real subsequent commit passes with the refreshed pin.
- Prepared recovery initially silently ignored a conflicting explicit destination, and install initially stepped over an unfinished retiring journal. Both public fault controls now refuse with phase-specific uninstall-then-install guidance and unchanged fingerprints, including the retiring journal's lock.
- Exact original local hooksPath comments and section order initially survived one full install/uninstall cycle but were reformatted on the second. A retired reinstall now captures the current original bytes directly; both complete cycles preserve the exact original bytes.

- Initial actual install/reinstall/commit/uninstall workflow failed with exit 3 `installation_activation_unavailable`; it now passes with clean commit admission, full staged-content secret rejection and original config restoration.
- Removing installed `scan_dispatch.py` initially made actual checkout fail via reference-transaction with exit 128. The repaired independent unrelated launchers allow checkout and original post-checkout behavior while commit remains denied.
- An actual push initially succeeded after inherited global hooksPath changed. The narrow relevant-hook selection guard now denies `hook_configuration_drift`; unrelated global `user.name` edits remain usable. Branch-dependent includes and rewritten destination configurations were also observed activating before their explicit pre-mutation refusals were added.
- An actual installed commit initially succeeded after the owner budget became mode 0666. Per-invocation protected private capture now rejects that trust drift; valid budget-content edits apply on explicit retry without reinstall.
- An 8000-entry mostly unchanged index plus one changed file passes the direct gate under a legal 1-MiB capture profile. The installed commit initially also passed despite combined parent/child capture exceeding that profile. It now denies `capture_bytes_limit` after composed accounting.
- Audit-hook injected Git-ancestor substitution at `tempfile.mkdtemp` initially created a preparation directory in a foreign target. Descriptor-relative staging now leaves the foreign inventory exactly unchanged and safely refuses.
- A later audit-hook substitution before private Git config editing initially removed a foreign fixture's hooksPath. The held-cwd child bridge now preserves those exact foreign bytes. The primary independently observed direct `/dev/fd/N` cwd fail with ENOTDIR and validated the bridge prototype; product proof is the public CLI fault case, not that prototype.
- Public prepared-worktree cancellation followed by uninstall initially failed with generic `installation_metadata_unsafe` for absent config.worktree. It now restores absence successfully and preserves shared config.

Some composed controls were added after working implementation and are not claimed as pre-change reds. One early PATH assertion compared against the calling environment rather than a real preinstall Git-hook baseline; Git itself prepends its exec path. That fixture was corrected to compare actual preinstall/installed observations. The first late-config fault fixture had invalid nested quoting, then a foreign file without the edited key; only the strengthened valid fixture demonstrated the real mutation above.

## Frozen input identity

Final neutral build: `82e125f8e74728baf01a0e1d792d4ec131f9a309d90b861b16287482dde9b029`. Exact closure: 22 assets, 19 `MODULES`. The original accepted T6 evidence is byte-identical: `c17fe12719d6338c758fc4169478fcdba78ddf486bb949f210797f7707205983`.

Earlier vertical slices used evolving source and are development observations, not final-build reruns. Broad compatibility build `dfccdd4d26cf12429443a5cc3488191d54fc473c36d840673283279d0e1fbc65` passed 54 focused cases per interpreter, an added duplex control, CLI/status/gates/LFS/installers. Build `726ac4472822aa30592be3f6f746b1d11876d520f809864fa4ca06f873f5af00` changed only retired original-byte selection and passed focused56 per interpreter plus installers/generator/recovery/registry. Build `61e423f4576a7b38ce49f643ff1999ddefce3087e2519f6626ca9f8b68b853e3` added strict malformed-owner admission and passed focused57 per interpreter. A subsequent Git-identity refresh slice passed focused58 per interpreter before the last recovery conflict refusals.

Compared with the broad compatibility build, only `scan_repo_install.py` and `scan_repo_state.py` changed: exact retired config restoration, malformed ownership admission, explicit trusted-Git identity refresh, and phase-aware conflicting recovery selection admission. The remaining 20 neutral inputs are independently byte-identical, including scanner policies, gates, dispatchers, budgets, held-cwd capture, native API and packaging runtime. Their broad results retain their original build attribution. Six provider metadata outputs were canonically refreshed; the three generated scan_git helpers remain byte-identical to that earlier compatibility build.

| Input | SHA256 |
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

## Verification

All fixture homes, repositories, bare remotes, data roots and recording endpoints were disposable/local. Actual recorded-endpoint LFS uses `/tmp/design-b-lfs-3.8.0/git-lfs-3.8.0/git-lfs`, the supplied official 3.8.0 temporary binary. No real home/repository was installed or external remote pushed.

| Check and build attribution | Observed result |
| --- | --- |
| Previous frozen build: repository preview/activation/recovery, Python 3.14.6 | 54/54, 53.936 s |
| Previous frozen build: same, Python 3.13.14 | 54/54, 52.639 s |
| Previous frozen build: added installed proc-receive duplex-timing control, both interpreters | 1/1 each; emits before input EOF, exact response and exit 7 |
| Previous frozen build: CLI compatibility, Python 3.14.6 | 35/35, 18.278 s |
| Previous frozen build: historical status compatibility | 29/29, 15.506 s |
| Previous frozen build: Git gates | 62/62, 48.476 s |
| Previous frozen build: verified LFS | 43/43, 68.871 s |
| Previous frozen build: neutral/main installers | 21/21, 40.449 s |
| Build726ac: focused recovery/activation, Python3.14.6 /3.13.14 | 56/56 each, 61.075 /59.454 s |
| Build726ac: full neutral/main installers | 21/21, 41.166 s |
| Build726ac: generator /full diagnostic recovery /registry | 26/26, 17.905 s /16/16, 66.604 s /14/14, 11.094 s |
| Build61e423: focused recovery/activation, Python3.14.6 /3.13.14 | 57/57 each, 62.350 /61.406 s |
| Subsequent Git-identity slice: focused, Python3.14.6 /3.13.14 | 58/58 each, 65.305 /64.290 s |
| Final build: focused repository preview/activation/recovery, Python3.14.6 | 60/60, 62.351 s |
| Final build: same, Python3.13.14 | 60/60, 58.576 s |
| Final build: generator | 26/26, 17.797 s |
| Final build: real main installer usable-neutral preflights | 1/1, 29.849 s |
| Final build: source-free exact-closure pre-commit/publication gates | 2/2, 0.880 s |
| Final build: source-free verified LFS delivery | 1/1, 1.556 s |
| Final build: missing-helper closure/healthy recovery | 1/1, 7.314 s |
| Final build: default provider capture compatibility | Codex, Copilot and Gemini PASS; block/warn, finite timeout/cancellation, native capture fallback, limits and audit controls |
| Final build: canonical freshness and whitespace | 62 generated files current; diff check clean |

The frozen focused cases cover source-free real neutral activation, removal of source AND neutral runtime followed by actual commit/push through repository copies; clean/intermediate-history secret push rejection with unchanged remote and zero downstream execution; standard LFS hook installation with zero endpoint requests/bytes before secret rejection and exact checked clean payload delivery; all 26 unrelated original-path binary protocol/argument/stdout/status cases; inherited relative/global includes; explicit worktree/sibling isolation; actual selected-index/partial commits; strict unknown/malformed ownership; hardlinks, changed/unknown owned files, held ancestry substitutions; safe original additions; idempotence and changed binding/reinstall after uninstall; private backups; and the long-path/all-28-present actual commit/uninstall control.

Cancellation/recovery faults are explicitly injected at Python OS audit boundaries around a real public CLI process. They cover durable preparation SIGINT, durable preparation SIGKILL, post-configuration-promotion SIGKILL and retiring uninstall SIGKILL. A real concurrent Git config writer fails under held config.lock without overwritten data; a second installer fails under installer lock. Exact journaled stale-lock recovery succeeds, while a foreign replacement lock remains fingerprint-identical. These are controlled process faults, not claims of an organically observed OS crash or universal power-loss atomicity.

An initial un-escalated CLI run could not invoke `ps` because of sandbox policy; it was an environment-limited run (35 tests, one infrastructure error), not a product pass. The scoped escalated frozen rerun above passed all 35.

The held-cwd implementation follows the documented POSIX descriptor inheritance and child process APIs: [Python subprocess](https://docs.python.org/3.14/library/subprocess.html), [os.fchdir](https://docs.python.org/3.14/library/os.html#os.fchdir). Configuration parsing and edits remain owned by [Git config](https://git-scm.com/docs/git-config/2.54.0).

## Integration and remaining boundaries

Delivery is one clean private scoped commit; the worker explicitly relinquishes ownership in its receipt. The primary must integrate serially, review this candidate and reconcile the ExecPlan/source maps/README/CI/KB. This worker does not mark a milestone accepted. Native Windows T7b-W, I3 production workload/capacity, real CI delivery and owner-only deployment remain separate. No claim is made that local hooks prevent intentional bypass or unrelated network tools.
