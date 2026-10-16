# W0 native installer repair evidence

Implementation and scoped verification are complete; primary review and integration remain. The private branch is unpushed, all owned processes have drained, and local test ownership is released. Primary owns plan/status reconciliation, integration, CI publication and the single coordinated knowledge pass. No live-home deployment occurred.

## Result and supported behavior

Two actual native failures prevented the real PowerShell installer from reaching its intended helper-error assertions. First, the held drive root was owned by TrustedInstaller, whose fixed Windows Resource Protection SID was absent from privileged ancestor trustees. Second, Win32 `SetFileInformationByHandle(FileRenameInfo)` returned error 87 during stage promotion. The final candidate recognizes the exact system SID for ancestors and uses explicitly typed `NtSetInformationFile(FileRenameInformation=10)` with the same held parent, source handle, no-replace flag, UTF-16 component and buffer layout. Native execution then passed the complete installer suite.

Private bundle files, directories, stages and locks still require exact current-user ownership and the existing single-owner full-control DACL. Unknown owners, ordinary-user dangerous effective/inheritable grants, unsupported ACEs, links/reparses, hard links and ownership drift retain their refusal paths. No path-based rename fallback or process-CWD change was added. Canonical `hooks/runtime/scan_native_file.py` is unchanged; its similar Win32 call needs its own public shared-path proof before repair. This installer result does not establish general native scanner, Git gate, status containment or provider-delivery acceptance.

The helper-error assertions retain all original conditions, genuine helper exit-2 stubs, real installer calls, no-stdout requirement and preflight home fingerprints. Failed assertions now include helper identity, installer exit and at most 2000 characters of each captured stream, replacing the disposable workdir with `<fixture>`. Temporary copied exception/owner tracing was removed. Two native real-installer controls grant Everyone effective or inherit-only WriteData on a disposable creation parent and require preflight rejection, no stdout, unchanged home bytes/tree and unchanged DACL.

## Actual native red and green

Every candidate below was committed privately and frozen before primary published an append-only snapshot with the exact same full tracked tree. Diagnostic trace output contained only bounded exception types, numeric codes, function/line IDs and known owner categories; it exposed no exception messages, personal SIDs, account names, locals or environment values.

| Private candidate | Published source snapshot | Shared full tree | Actual Windows run and observed result |
| --- | --- | --- | --- |
| Baseline | `d8d58e0814f7c3e1ef4fe766db555eef1bd3aa79` | Baseline source | [38978729929](https://github.com/japurcell/skills/actions/runs/38978729929), job `117234305423`: original missing helper diagnostic assertion, exit 1, 22:58:00 UTC. |
| `8b33dec65edf5a4f0827391317db0be0696c1d8c` | `71def2b1d68241909f706b1db9beba96100928a6` | `9555592b9635dc528e22957f1f35f1993c3e9169` | [38979365490](https://github.com/japurcell/skills/actions/runs/38979365490): `configure-rtk.py` iteration never reached its stub; earlier neutral scanner dry-run failed, exit 2, 23:04:44 UTC. |
| `0650e88542826664f76a2181a0a742a48546323e` | `285f5bcf75e1c4ec23bbcae1448c1e201c4d3b9c` | `55e942334a52ff34e1c2ed679676db8047b78374` | [38979738312](https://github.com/japurcell/skills/actions/runs/38979738312): `OSError`, no numeric error, `main:406>install:342>private:91`; explicit drive-root owner refusal, 23:08:31 UTC. |
| `312e4a5aa67a01a93445af014db6ba97a5b2d61e` | `898d8f63c311f9a4ae8b2d01a8246d00cbf8bf6b` | `bffb369696de26da7b35e74e1512a549a1fe2e27` | [38980193042](https://github.com/japurcell/skills/actions/runs/38980193042): `Fixture drive-root owner category: trustedinstaller`, followed by the same owner refusal. |
| `339bbe3494240cfbf164818fbb611be915bc881d` | `0c2282f4c0f42681c229aa4bcad6a09026707f90` | `a8ca31973d5bd56b4b8a8a33a5ac9091a7321ee5` | [38980469537](https://github.com/japurcell/skills/actions/runs/38980469537): root repair passes dry-run, RTK and freshness 65; later neutral deployment fails in `install-codex-agents.py` iteration, 23:16:47 UTC. |
| `b16a93b4d25d9c064cbf5247a1e8702cbeaefff2` | `5519eb667659e2c3e29464d2929b4da65881d04b` | `95bf8fbf3475766fb41d0f0e60e807c2246ebe46` | [38980987771](https://github.com/japurcell/skills/actions/runs/38980987771): `OSError winerror=87 errno=22 frames=main:406>install:391>rename:254`, no chained error, 23:22:28 UTC. |
| `2c1ff0fb4a3d27b91091a0dd36750b626f65a302` | `700c6e7774a275b3854e1d9f4e997f342abc13f3` | `6d7cee965edd509eb1b1243deab2fe78f1e5306c` | [38981299888](https://github.com/japurcell/skills/actions/runs/38981299888), job `117242529406`: complete native PowerShell installer succeeds. Later generated native capture fails separately; this is not a whole-job pass. |

All times above are on 2026-10-16. The successful job recorded Windows Server 2025 `10.0.26100`, image `windows-2025-vs2026`, Git `2.56.0.windows.2`, CPython `3.13.16`, and stable RTK `0.50.0`. The installer has 39 top-level invocations; Windows explicitly excludes POSIX directory/file modes, unreadable-000 copy-failure assertions and executable/Unix-mode assertions. Its native ACL and junction cases are not excluded. Safe proof excerpts from the completed step:

```text
23:25:29.0748942Z Run pwsh -NoProfile -File scripts/test-install.ps1
23:25:47.7976860Z Native scanner ACL controls: effective and inherit-only ordinary-user write grants rejected without mutation.
23:29:02.7318757Z test-install.ps1: all tests passed.
```

The observed log span is 213.657 seconds (step metadata rounds to 213 seconds). Read with `rtk proxy gh run view 38981299888 --repo japurcell/skills --job 117242529406 --log`; retain only the installer receipt when attributing W0 acceptance. The native comparison supports the Win32-wrapper mismatch inference for this exact held-parent call; it is not a universal claim about all Win32 rename forms.

## Final POSIX compatibility and frozen inputs

W0 composed accepted base `b24757a4`, including T8b `4e7f42761adc53137ca9c6300c7b2fc7851a90b6`, before the green native and final local checks. All accepted T8b installer expectations remain intact. The final serial checks ran on the same frozen functional source `2c1ff0fb4a3d27b91091a0dd36750b626f65a302`, with Python 3.14.6, PowerShell 7.6.7 and Bash 3.2.57 on macOS:

| Exact command from private repo root | Observed result | Process time |
| --- | --- | --- |
| `rtk proxy pwsh -NoProfile -File scripts/test-install.ps1` | Exit 0; 39 top-level invocations, explicit Windows-DACL and unavailable-junction exclusions | 280.131 s |
| `rtk proxy bash scripts/test-install.sh` | Exit 0; all 34 top-level cases | 86.240 s |
| `rtk proxy python3 -B scripts/test-install-scan-secrets.py` | Exit 0; all 25 tests | 53.876 s (unittest 53.835 s) |

The runner wrapped the exact commands with RTK and retained `/tmp/design-b-w0-final-results.json` and `/tmp/design-b-w0-final-{powershell,bash,neutral}.log`. Before and after, all 3447 tracked files had identical SHA-256 bytes, types and Unix modes. Both sorted input receipts, `/tmp/design-b-w0-final-inputs-before.json` and `/tmp/design-b-w0-final-inputs-after.json`, have SHA-256 `4f6307e8c95ec03b4f32418392204e70c304406d3dd103774bb3bdb8c407402f`. No generator or additional functional group ran concurrently. The process session returned exit 0 and EOF before ownership was released.

A preliminary PowerShell pass on earlier root-only repair `339bbe34` took 278.375 s; its `/tmp/design-b-w0-powershell.{json,log}` receipts are historical compatibility evidence, not proof for the later rename change.

Relevant final bytes and POSIX modes, identical to the native-tested functional tree:

| File | SHA-256 | Mode |
| --- | --- | --- |
| `scripts/scan_install_windows.py` | `68636a86f050fc9ea1e0e1c8189720fe9cd627bdeb2c637ecbe6d3bf0b4f5640` | 644 |
| `scripts/test-install.ps1` | `3c6dd01f06c637c9f6ca8dd756572e4bf7b49701149ba55f99e9c2909d8fa934` | 755 |
| `scripts/install.ps1` (unchanged) | `664486797aff7148c4892aae479591e9b2c520845881101eaf3f5a2fada45174` | 755 |
| `scripts/install-scan-secrets.py` (unchanged) | `87548dce0e704a32a45d436f69df7efc1e0782e20a09d537c045d0cc65e0a7be` | 755 |
| `scripts/test-install.sh` (unchanged) | `240d54a97cfaf93dedf8437dc2a8986e155b1f8d007fbeff4107abd2f9830cf6` | 755 |
| `scripts/test-install-scan-secrets.py` (unchanged) | `7039f15a455bab84344f53f67d740dbab34bb95ee5b32a29288c55c83517bb04` | 755 |

The final history consolidation changes only this evidence relative to the frozen green candidate; executable, configuration and test inputs stay exact. The private result contains only `scripts/scan_install_windows.py`, `scripts/test-install.ps1` and this evidence file relative to its accepted base.

## API basis, review and remaining ownership

Microsoft documents the fixed TrustedInstaller service SID and protected-system ownership in [Windows file and registry permissions](https://learn.microsoft.com/en-us/archive/msdn-magazine/2008/november/access-control-understanding-windows-file-and-registry-permissions); the [Server 2025 SID reference](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/manage/understand-security-identifiers) establishes system/service identity. The [NtSetInformationFile contract](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/ntifs/nf-ntifs-ntsetinformationfile) specifies the user-mode Nt name, IO_STATUS_BLOCK, class 10, signed NTSTATUS and DELETE requirement. [FILE_RENAME_INFORMATION](https://learn.microsoft.com/en-us/windows-hardware/drivers/ddi/ntifs/ns-ntifs-_file_rename_information) specifies the held RootDirectory and simple relative name. [Set-Acl](https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.security/set-acl?view=powershell-7.5) and [file rights](https://learn.microsoft.com/en-us/windows/win32/fileio/file-security-and-access-rights) support the disposable negative fixtures.

Five-axis self-review found the fix narrow, readable, within installer ownership, bounded and without extra dependencies or runtime loops. It preserves exact leaf ownership, namespace anchoring and existing negative assertions. Primary independently reviewed candidate source and observed the native installer pass; final integration review remains primary-owned. The canonical shared-helper rename, later generated native capture failure, broader native installation/security matrix, live provider delivery and any deployment remain separate work. K1 is primary's coordinated end-of-session knowledge pass; this worker made no KB changes. No durable in-scope skill improvement was identified.
