# T6a, qualify the filesystem adapter

The installer maintainer and a Windows runner compare a disposable prototype with the existing `Copy-Skills` path. Have the Python traversal classify links/reparse points without following them, omit excluded subtrees before enumeration, and produce an ordered stream of operations for a skill. Keep the PowerShell process alive for one skill to perform native link/junction creation, copying and mode handling. Feed a single operation sequence using structured JSON and literal paths, with success/failure reported by the native adapter. Compare the destination tree, link and junction targets, modes and failure cleanup with the existing installer. Stop after recording native results. If the candidate cannot preserve a behavior, keep the existing caller active, record the failed case and revise the adapter before switching it.

The installer maintainer owns a disposable proof for the shared traversal/native adapter. Compare the actual PowerShell entry point on the current platform and native Windows controls per the milestone. Record exact commands, platform, file/target/mode readback and blockers. Keep the shipping callers active until qualification.

Use the [milestone contract and verification commands](6-skill-copy.md) and the [integration plan](../ExecPlan.md). Record results and remaining evidence here.

## Local prototype and result (2026-11-19)

The experimental implementation is `scripts/tests/installers/adapter-prototype/`: `copy.py` produces one ordered JSON operation sequence per skill using the existing `filtered_entries` policy and classifies links/reparse points before descent. `adapter.ps1` starts once, reads that sequence, uses native PowerShell installer functions and restores directory modes on failure. It unlinks existing symbolic links through .NET before creating a new link: `Remove-Item -Force` changed a target inode's mode in the failing case below. The prototype is test-only and is not a replacement for the public installer. The existing pruning helper is invoked separately after the prototype copy in the comparison. Addy profile and all production callers remain unchanged.

From the checkout root, run:

```bash
rtk proxy python3 scripts/tests/installers/adapter-prototype/test_prototype.py
rtk proxy python3 scripts/tests/installers/adapter-prototype/compare.py
```

On macOS 27.2.1, Python 3.14.6 and PowerShell 7.7.0, both commands exited 0. The first test audits `os.scandir` calls and confirms the excluded `__pycache__` subtree was never enumerated. The comparison copies a checkout to a disposable directory, adds a visible skill fixture and invokes the actual Bash and PowerShell entry points in separate homes twice; it invokes the prototype and existing prune in a third home. It compares every relative path, file content, mode and link target after each run. Its fixture includes `README.md`, `evals`, a conventional test script, a cache subtree, `nested/odd [x].txt` (mode 0451), relative file and directory links, a dangling link, and a destination-only note. All three readbacks agree: the excluded paths are absent, the note remains, the file has mode 0451, and `link` targets `nested/odd [x].txt`. It then replaces the file in each destination with a read-only hard link to an external file, makes the skill directory 0555, and requires exit 1, unchanged external content and 0444 mode, same inode, and restored 0555 directory mode. Logs and individual JSON readbacks survive at `/private/tmp/adapter-compare-ri5yo7dl`; the script prints its new evidence directory on each run. The optional `ADAPTER_SCAN_TRACE` environment variable records actual enumerated directories as JSON lines.

The first negative run failed: `/private/tmp/adapter-compare-dnvorxqi` records that both public installers refused the hard link but the initial prototype exited 0 and changed the external inode mode to 0644. The preceding link replacement used PowerShell `Remove-Item -Force`; the corrected .NET unlink and repeated fixture passed. Do not discard this failure when revising the adapter. A `verify-skills` Doctor on the checkout passed; evidence is at `/private/tmp/verify-m6.NPEfPD/evidence/doctor.txt`.

**Remaining qualification:** this is local POSIX evidence only. It does not establish Windows symlink, junction, unsupported reparse-point, ACL, or native failure behavior. The prototype's Windows .NET unlink branch requires a real Windows run. T6b must preserve the failure and cleanup cases and prove its two profiles and public reinstallation before switching callers. M6 remains open pending that work and native Windows qualification.

The original Addy, Bash and PowerShell installer fixture suites exited 0 on the same host; PowerShell reported its native junction test skipped on macOS. These runs preceded the fast-forward to integration revision `71513b21`, which does not change the installer files.
