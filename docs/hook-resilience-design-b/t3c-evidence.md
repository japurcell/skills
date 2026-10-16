# T3c installed checkpoint evidence

Date: 2026-10-16 UTC. Private branch `codex/design-b-t3c`, starting at `91d1b31`. All homes, configuration, data, repositories and fault markers used disposable locations. No live installation, provider/Git activation, push or publication occurred. The primary owns plan, registry, CI and the coordinated KB pass.

## Delivery

`scripts/install-scan-secrets.py install` explicitly deploys the exact source-derived standalone closure: entrypoint, CLI, status and the ten `scan_cli.MODULES` modules, thirteen files total. It captures the CLI once for both dependency extraction and deployed bytes. The pristine prerequisite native helper had SHA-256 `660222d89c1b01d3ef77a34920362c99d2567a11c98cdddc24db542e34a788fb`; this is evidence, not a permanent content pin. Captured delivered bytes and manifest hashes bind the installed build, and packaging validates the small public handle API while allowing compatible optional additions. No canonical runtime or generated provider output changed.

Default executable location is `$HOME/.local/lib/scan-secrets` on Unix/macOS and `%LOCALAPPDATA%/Programs/scan-secrets` on Windows. No PATH or profile edits occur. Invoke the absolute `DESTINATION/scan-secrets` shell launcher on POSIX, or `pwsh -NoProfile -File DESTINATION/scan-secrets.ps1` on Windows. These launchers pin the resolved absolute Python interpreter and installed entrypoint and request `-I -S -B` at the first Python process boundary. The PowerShell launcher forwards `@args`; there is no batch `%*` expansion. Installed layout preserves `ENTRY.parent.parent/hooks/runtime` and retains no source/provider link.

The owner-only installation manifest records exact asset/launcher hashes, absolute interpreter/entrypoint/runtime/data locations and `configuration: null` (built-in policy; no trusted configuration binding selected here). Direct check/status keep the documented platform data-root selection; future gates must consume explicit pinned bindings. Reports/audit stay outside executable storage. Runtime checks do not write bytecode or executable assets.

Both real platform installers preflight the new exact runtime and packaging-support source before destination mutation, then invoke explicit neutral installation in their authorized existing installation flow. Existing provider closures/configuration behavior is preserved. `scripts/scan_install_windows.py` is installer-only support, captured and compiled explicitly even in POSIX preflight, and included in both reduced installer source fixtures; it is not part of the thirteen-file runtime bundle.

## Public red to green

A prerequisite fingerprint was initially mistaken for a permanent installation pin. A retained public compatible-helper-update control failed with `source_assets_invalid` before removing that overconstraint; it then passed install/check/status with exact updated bytes recorded in the manifest. Missing/syntax/unsupported-API negatives remain required. Current-source main-installer evidence exercises unchanged accepted source inputs; revised future-compatible behavior has its own focused proof.

The first `rtk proxy python3 -B scripts/test-install-scan-secrets.py` failed at the real helper process with missing `scripts/install-scan-secrets.py`. After implementation, the installed help process passed. A second public reproducer created a private destination containing unrelated `owner-notes.txt`: before repair installation returned zero and removed that file. Its retained test now requires refusal and byte/mode preservation for both an unowned destination and unowned sibling `.previous` tree.

The final focused suite has twenty-one public-process tests. It covers:

- Installed help/version/help-command, clean check and historical status through both shell and PowerShell launchers, findings and incomplete check exits, source checkout removed, no provider-tree dependency, paths containing spaces and shell metacharacters, host PYTHONPATH/sitecustomize sentinel untouched, redaction and no bytecode.
- Read-only dry-run and no-argument/help/version, rejected unknown/abbreviated arguments with no reflected fake credential, one versioned JSON result, safe errors, open stdin and bounded broken-output behavior.
- Exact missing/corrupt runtime, unsupported native helper API, packaging-support omission/corruption, FIFO and oversized source failure; no destination changes. Existing data is preserved on linked/hardlinked targets and unrelated owner files/directories. Public writable-parent and writable-ancestor controls are refused; an owner-private child under the standard root-owned sticky temp root remains supported.
- Idempotent reinstall and interrupted `.previous` recovery. Activated OS audit controls fail once at actual stage promotion after the old bundle rename, for ordinary failure and Ctrl-C; exits are respectively two and 130, and the old complete fingerprint remains. An actual hard kill at that paused boundary proves a concurrent install reports busy and the next explicit install recovers after kernel lock release. No private installer function or rollback implementation is substituted.
- Activated destination-ancestor substitution at the real temporary-stage operation: mutations remain in the held directory, the substituted external directory bytes/modes are unchanged, and promotion fails safely with `unsafe_destination`.
- Both real main installers install usable neutral launchers with the source hidden, and both reject missing status before home mutation. Full-repository PowerShell installation has a finite 120-second fixture bound; check/status/helper bounds remain tighter. An earlier 30-second full-install fixture timeout under concurrent installer load was corrected by serializing final installer runs and using that appropriate full-install bound.

Source-admission boundary controls also reproduced and repaired two first-install inconsistencies. A 59-asset closure initially installed despite exceeding the ownership reader's 64-entry ceiling on later inspection; admission now requires runtime assets plus the six fixed directory/launcher/manifest entries to fit the same limit. The exact supported boundary is 58 runtime assets and 64 total entries: first install, identical reinstall and installed clean check pass. Oversized or duplicated/reserved module names are rejected without writes. Case-only and canonically equivalent Unicode spellings initially reached staging and failed after creating lock state; a single NFD-plus-casefold key now rejects those aliases in source preflight. The current canonical thirteen-asset input is unchanged by these predicates.

The full Bash/PowerShell/RTK-stable results used the accepted canonical thirteen-file closure. Subsequent admission-only repairs preserve that exact successful input and byte-for-byte runtime payload; the final focused suite re-exercises both real main installers with the final helper and tests each revised negative/compatible boundary. No unchanged broad suite result is presented as proof of the new boundary cases.

## Transaction and recovery boundaries

Existing destination/backup replacement requires the exact schema, bindings, owned inventory and stored hashes. Unexpected names, edited owned files, unsafe types/permissions, links/reparses and hardlinks fail closed. Regular-file input reads use no-follow/nonblocking descriptors where supported, verify regular/single-link identity, and read at most one MiB plus one byte. Private bundle inventory is bounded to 64 entries and ten seconds.

POSIX mutations use names relative to a held, component-verified no-follow parent directory and restore the caller's original CWD. Executable ancestry must be root/current-owned and lack ordinary-user write access; the root-owned sticky-directory exception requires the following protected owned child, and the final parent must be current-owned without group/other writes. An immediate advisory lock serializes installation; its stable owner-only sibling `.install-lock` file remains, while process termination releases ownership. Ordinary promotion failures restore the previous directory. A hard kill can leave a private `.scan-secrets-stage-*` directory and/or a complete `.previous` bundle; the next explicit install validates and recovers the backup. Orphan stages are not executed or blindly deleted. Unknown or edited backup ownership requires owner inspection and repair, not an automatic overwrite.

Windows packaging uses the unchanged captured `WindowsDirectoryHandles` boundary for component traversal and child opens. Owner/protected-DACL checks and updates use handles; ancestor ownership/access recognizes current account, SYSTEM and Administrators as privileged trustees, rejects effective ordinary-user dangerous grants, and additionally rejects dangerous inheritable/inherit-only grants before creating a child, lock or stage; staging writes, bounded inventory, directory-relative promotion and leaf-first exact-owned cleanup use held handles. There are no path-based Windows DACL setters, external ACL executables or sharing-only anchoring claims. Windows inventory is bounded to 64 entries, one MiB of enumeration buffers per directory, and a ten-second operation deadline with bounded recovery cleanup.

## Verification

Run from the private worktree root with RTK, protected Python where applicable, and isolated homes. Final installer suites run serially.

- `rtk proxy python3 -B scripts/test-install-scan-secrets.py`: 21 tests pass (40.744 seconds). The preceding 18-test compatible-update suite passed in 38.795 seconds; the final suite includes capacity and portable-name admission controls.
- `rtk proxy python3 -B scripts/test-scan-secrets-cli.py`: 35 tests pass (18.748 seconds). Initial sandbox run failed at real `ps` with EPERM; the unchanged test was rerun with narrowly scoped process-observation escalation and passed.
- `rtk proxy python3 -B scripts/test-scan-secrets-status.py`: 29 tests pass (15.209 seconds).
- `rtk proxy bash scripts/test-install.sh`: full suite passes, exit 0.
- `rtk proxy pwsh -NoProfile -File scripts/test-install.ps1`: full suite passes; host explicitly cannot create junctions, so native junction proof remains pending.
- `rtk proxy python3 -B scripts/test-rtk-stable.py`: 12 tests pass (21.779 seconds).
- `rtk proxy python3 -B scripts/test-generate-hooks.py`: 26 tests pass (17.860 seconds). The unchanged source-mutating suite first hit sandbox EPERM in five fixture-mutation cases; narrow private-worktree write escalation reran all 26 successfully.
- `rtk proxy python3 -B scripts/generate-hooks.py --check`: all 62 generated outputs current. No runtime/generated file remains changed.
- Python compilation and Bash/PowerShell parse checks pass; staged whitespace check is recorded with the private commit.

Transient complete logs are `/private/tmp/t3c-verified-focused.log`, `/private/tmp/t3c-verified-bash.log`, `/private/tmp/t3c-verified-powershell.log`, plus `/private/tmp/t3c-complete-focused-21.log` and `/private/tmp/t3c-accepted-generator.log`.

## Official API basis and remaining platform proof

The Microsoft documentation establishes API signatures and structure layout, not a native Windows execution result:

- [GetFileInformationByHandleEx](https://learn.microsoft.com/en-us/windows/win32/api/winbase/nf-winbase-getfileinformationbyhandleex) documents directory classes `0xa` and restart `0xb` and resuming enumeration on the same handle.
- [FILE_ID_BOTH_DIR_INFO](https://learn.microsoft.com/en-us/windows/win32/api/winbase/ns-winbase-file_id_both_dir_info) supplies the layout and eight-byte record alignment. Name bounds use UTF-16 byte lengths.
- [FILE_RENAME_INFO](https://learn.microsoft.com/en-us/windows/win32/api/winbase/ns-winbase-file_rename_info) documents a held RootDirectory for relative destination resolution and byte-counted file names.
- [GetSecurityInfo](https://learn.microsoft.com/en-us/windows/win32/api/aclapi/nf-aclapi-getsecurityinfo), [SetSecurityInfo](https://learn.microsoft.com/en-us/windows/win32/api/aclapi/nf-aclapi-setsecurityinfo), and [GetTokenInformation](https://learn.microsoft.com/en-us/windows/win32/api/securitybaseapi/nf-securitybaseapi-gettokeninformation) establish handle-based descriptor and process-token APIs.

Execution here is macOS/POSIX, including real `pwsh` on macOS. Native Windows DACL, junction/reparse races, directory enumeration/promotion/cleanup, msvcrt locks, argument forwarding and cancellation remain **UNVERIFIED** until T9c/V1. A macOS PowerShell pass is not NTFS proof. T7 owns repository/Git gates and pinned gate binding; I2 owns suite registry and combined acceptance; T8 owns provider lifecycle changes. No saved status authorizes publication.

## Frozen source SHA-256

- `scripts/install-scan-secrets.py`: `97d7edeaca305ba47edc7acb8c8d4208dee4d1ede08faf1d8d8e42fee7c07ed0`
- `scripts/scan_install_windows.py`: `c0cb6161cdf6d9b0bf2bb2c1899a23ff6f87d62cfcf6a541b9a61dc0b88af3f0`
- `scripts/test-install-scan-secrets.py`: `61e36f3d79f5afe2df1c8662c5fa40b8c33330a6506bd31622d7820b79c8cb04`
- `scripts/install.sh`: `69d59fbaf1a205d992c503280cf99a952bb6c396eafdebc67043323cc7205f70`
- `scripts/install.ps1`: `c2d41871a1084df0ba86403b476484527da2e8427ac2898f606772700f2c73e4`
- `scripts/test-install.sh`: `7cb618ac2eaf4f9a74ff30a0a4dfdc6a129152a6903f1659073ad7f8466d7625`
- `scripts/test-install.ps1`: `4ccb2362b5d5f1e68a6484aa0d2f99bb65b01fc5891e17699c42235d1b1c01d8`
