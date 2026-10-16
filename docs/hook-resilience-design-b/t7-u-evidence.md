# T7-U: Prior neutral installation upgrade evidence

Observed 2026-10-16 on macOS 26.7.1 arm64. Worktree: `/Users/adam/.codex/worktrees/design-b-t7-u/skills`; branch: `codex/design-b-t7-u`; starting commit: `d3eb6131b3da60929c0e2173ccacab8c747c3601`. All installation, corruption and recovery fixtures used disposable homes. No live-home deployment, external publication, runtime change, native Windows acceptance or combined I3 acceptance is claimed. The primary owns plan reconciliation, integration and the single coordinated KB pass.

## Outcome and boundary

The current neutral installer now admits an intact prior owned closure independently of the desired new payload. It reads the old protected `scan_cli.py` as data, verifies its recorded hash, and accepts exactly one literal `MODULES` tuple with validated names, uniqueness, normalized case/Unicode collision refusal, reserved-name refusal and the shared 64-entry inventory cap. The source admission path uses the same parser. No prior runtime import or execution establishes ownership.

The prior manifest still requires its exact schema/version, destination binding, absolute interpreter/data paths, null configuration, typed file/launcher maps, lowercase SHA-256 digests, canonical launcher bytes/binding, complete inventory and matching file hashes. The existing bounded no-follow single-link regular-file reads, private ownership/modes, bounded walk, ancestor trust, installer locks and backup/promotion logic remain intact. Unknown manifest paths, extra declared or undeclared content and missing closure members fail before mutation. The Windows facade and its positional callback contract are unchanged; no native execution result is inferred.

This retains the existing local ownership trust model: restrictive filesystem ownership plus the stored manifest and recorded runtime declaration. It is not a release-signature system and does not authenticate a self-consistent rewrite by the trusted local owner. Arbitrary simultaneous direct-editor replacement remains outside D2; cooperating writers retain the existing locks, drift refusal and backup/recovery guarantee.

## Genuine red before implementation

Before source edits, the real I3-P public-process reproducer installed accepted T6 through its actual old installer into a disposable home, deleted the old source copy, and invoked the current installer against that same destination. The old install succeeded with 19 assets; the upgrade returned exit 2.

```text
rtk proxy python3 /Users/adam/.codex/worktrees/design-b-i3-p/skills/docs/hook-resilience-design-b/i3-p-probe.py \
  --source /Users/adam/.codex/worktrees/design-b-t7-u/skills \
  --output /tmp/t7-u-original-red.json --case upgraded
prior neutral: outcome=installed asset_count=19
current install: exit=2 outcome=incomplete reason=installation_ownership_invalid
```

The probe hash was `bcfaf55df4731b3bce6db13dd092b7b4e4f66c9aafb4b73b8165a057e09d63f2`; original installer hash was `97d7edeaca305ba47edc7acb8c8d4208dee4d1ede08faf1d8d8e42fee7c07ed0`. Its receipt records Python 3.14.6 and starting commit above. Raw machine receipt remains at `/tmp/t7-u-original-red.json`; the decisive transcript is retained here so this evidence does not depend on temporary-file retention.

The new regression was then run before changing the installer:

```text
rtk proxy python3 scripts/test-install-scan-secrets.py \
  InstalledScannerTests.test_actual_prior_releases_upgrade_without_old_or_new_source -v
Ran 1 test in 0.298s
FAILED (failures=2)
t6: current --dry-run returned 2 installation_ownership_invalid
t7a: current --dry-run returned 2 installation_ownership_invalid
```

An initial test draft reused the destination after the expected T6 failure and contaminated the T7a setup. Each release was assigned its own destination, then the isolated two-release red above was observed before the product edit. That failed draft is not counted as independent T7a evidence. After the minimal reader fix the same test passed in 1.941s.

## Actual immutable release fixtures

`scripts/fixtures/scan-secrets-releases/` contains deterministic USTAR/gzip captures of exact file bytes from the actual accepted commits. Capture used local `git show REV:PATH` and `git ls-tree REV -- PATH`; it did not derive historical modules from current source. Each archive contains only its old installer, native facade, entrypoint and exact declared runtime closure. `provenance.json` records every original path, mode, byte count and SHA-256, the historical module tuple, revision and archive digest. Tests pin both archive digests, validate contents/modes against provenance, invoke the genuine archived installer and delete its source before upgrade. Tests perform no historical Git lookup or network fetch. The primary independently compared all 43 captured files and modes to the accepted Git blobs.

| Release | Exact accepted revision | Runtime inputs / MODULES | Runtime build |
| --- | --- | --- | --- |
| t6 | `342287dde89ec772293b4c3df24a7a80cb216a22` | 19 / 16 | `baa8dc584d3c4e3edeadc787975b48e824c311b90aa80347f5a252b657b4dc3b` |
| t7a | `37ebafcc1330a99fd5a1a419a9725d026f85dd8c` | 20 / 17 | `7fde2f03ce5c3fa1e06235b83b87061b92a0ca5022578947f512ca0f7f2122b9` |


## Observed green verification

Runs were serial and completed while I3-P timed probes were quiet. Commands ran from the worktree above through `rtk proxy`. No tests were deleted, disabled, skipped or weakened.

| Command | Observed result | Suite seconds / wall seconds |
| --- | --- | --- | --- |
| `/Users/adam/.pyenv/versions/3.14.6/bin/python3.14 scripts/test-install-scan-secrets.py -v` | 25 tests, OK, exit 0 | 51.240 / 51.281 |
| `/Users/adam/.pyenv/versions/3.13.14/bin/python3.13 scripts/test-install-scan-secrets.py -v` | 25 tests, OK, exit 0 | 52.757 / 52.795 |
| `/Users/adam/.pyenv/versions/3.14.6/bin/python3.14 MINIMAL-COPY/scripts/test-install-scan-secrets.py <the four new test names> -v` | 4 tests, OK, exit 0 | 11.290 / 11.330 |

Python builds were `3.14.6 (main, Jul 30 2026, 16:35:50) [Clang 21.0.0 (clang-2100.1.1.101)]` and `3.13.14 (main, Jul 31 2026, 12:59:02) [Clang 21.0.0 (clang-2100.1.1.101)]`. Python 3.13 resolved to `/Users/adam/.pyenv/versions/3.13.14/bin/python3.13` through the requested `bin/python3` entrypoint. Complete disposable logs/receipts remain under `/tmp/t7-u-runs/`; the test source and results retained here establish the reproducible contract.

The four new public tests are:

- `test_actual_prior_releases_upgrade_without_old_or_new_source`: real T6 and T7a old installations; old source removed; no-write dry-run; real upgrade to 22 inputs; identical reinstall; new source removed; installed clean scan and status.
- `test_prior_release_drift_and_unknown_inventory_preserve_both_locations`: 13 damage forms at destination and `.previous`, each refused by dry-run and real install with the complete root fingerprint unchanged. Forms are edited/missing content, self-consistent missing-record/file pair, undeclared extra content, declared foreign content, traversal record, exposed mode, symbolic/hard links, malformed digest/map, forged-but-rehashed launcher, unknown owner schema.
- `test_prior_runtime_closure_must_be_one_complete_bounded_literal`: 11 malformed or ambiguous declarations, including non-tuple/nonliteral/type, duplicate/case/Unicode collision, reserved/traversal names, over-capacity and duplicate assignment; prior declaration hash is updated to exercise parser refusal independently of hash mismatch.
- `test_prior_release_recovery_never_executes_prior_runtime`: both genuine releases survive an actual intercepted promotion failure byte-for-byte; retained old-only `.previous` validates without mutation and recovers to current; process audit refuses any execution from the prior installed path and observes none.

The minimal-copy run included only current runtime files, four required script files and the immutable fixture directory; it asserted `.git` absent before running all four tests. It passed without historical objects. Full suites also retained the existing maximum 64-entry closure, compatible helper update, source-free POSIX/PowerShell launcher behavior, both real Bash/PowerShell main installers, no-write parser/preflight, unsafe source/destination/link/ancestor controls, exact backup ownership, interruption, hard-kill/kernel-lock recovery and bounded I/O controls. This PowerShell-on-macOS proof is distinct from native Windows. The new negative matrix and captured archive mode assertions establish POSIX/macOS behavior only: `chmod(0644)` tests exposed POSIX permissions, not a Windows DACL change. Native ACL equivalents remain unverified and belong to the separate native delivery/testing work.

Additional observed checks: `rtk proxy python3 scripts/generate-hooks.py --check` exited 0, `Generated hooks are current (62 files).`; `rtk proxy git diff --check` exited 0. No broad runtime benchmark or unrelated suite was rerun solely for this ownership reader change.

## Exact source and fixture identities

| File | SHA-256 |
| --- | --- |
| `scripts/install-scan-secrets.py` | `87548dce0e704a32a45d436f69df7efc1e0782e20a09d537c045d0cc65e0a7be` |
| `scripts/test-install-scan-secrets.py` | `7039f15a455bab84344f53f67d740dbab34bb95ee5b32a29288c55c83517bb04` |
| `scripts/scan_install_windows.py` | `c0cb6161cdf6d9b0bf2bb2c1899a23ff6f87d62cfcf6a541b9a61dc0b88af3f0` |
| `scripts/fixtures/scan-secrets-releases/provenance.json` | `575e79364fb230b38c3afdc99e6b82c5d185fd4a460715af5fc9402373fbd85d` |
| `scripts/fixtures/scan-secrets-releases/t6.tar.gz` | `04d1d01ca62b0d6ac0e1a6cf7c8b72c8315c867e515a11b62ba4dba1d3191258` |
| `scripts/fixtures/scan-secrets-releases/t7a.tar.gz` | `29eac6f655a5c34f207e3d760ad7503df89f2db18df3c1714a477a8b1da0c12e` |


## Frozen current runtime preservation

The ordered 22 current runtime inputs / 19 `MODULES` recompute to build `82e125f8e74728baf01a0e1d792d4ec131f9a309d90b861b16287482dde9b029`, exactly the accepted frozen I3 runtime. For each input below, its candidate bytes were also compared with `git show d3eb613:PATH` and matched. Neither `scripts/scan-secrets.py`, any runtime input, generated file nor `scripts/scan_install_windows.py` changed. The build is SHA-256 over each ordered basename, a NUL byte, and its exact raw bytes, matching the production build framing.

| Ordered runtime input | SHA-256 |
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


## Review and remaining acceptance

Self-review covered correctness (prior/current closures separated with exact rejection), readability (one shared literal parser), architecture (installer reader only, callback preserved), security (protected data-only prior declaration, complete schema/inventory/digest/path/link/mode gates) and performance (existing 1 MiB file, 32 KiB manifest and 64-entry bounds retained). No new dependencies were introduced. The primary has read-only reviewed the bounded reader change and independently verified fixture provenance; final acceptance remains primary-owned.

All repair test processes are finished. I3-P must independently rerun its previously blocked actual upgrade and integration workflows against the accepted repair; its existing capacity receipts can retain the unchanged runtime identity while clearly distinguishing the changed installer hash. Native Windows delivery and combined acceptance remain separate. No knowledge files, plan, registry, CI, README, generated or live installed files were changed by this owner.
