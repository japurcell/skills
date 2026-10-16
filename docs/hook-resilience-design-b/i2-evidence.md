# I2 source and installed CLI composition evidence

Date: 2026-10-16 UTC. Private branch `codex/design-b-i2`, starting at `7d3e7983`. This node changes only the explicit aggregate registry, its public coverage test, and these retained integration artifacts. The primary owns milestone acceptance, plan/README/CI updates, serial integration and the single final KB pass. No canonical runtime, installer or generated output changed.

## Registry red to green

The public `test-all.py --list` coverage test was extended to require the three already-maintained suites. Before the registry edit, `rtk proxy python3 -B scripts/test_test_all.py -k test_list_covers_maintained_suites_without_running_them` failed in 0.031 seconds, naming exactly `test-scan-secrets-cli.py`, `test-scan-secrets-status.py` and `test-install-scan-secrets.py` as absent. The registry now invokes each with `python3`, and the coverage test requires those exact commands as well as complete path equality and no duplicates. The public list contains 56 commands, up from 53. No discovery, subset flag or runner refactor was added.

## Retained public-process composition

From this worktree root, run:

```sh
rtk proxy python3 -I -S -B docs/hook-resilience-design-b/i2-probe.py
rtk proxy /Users/adam/.pyenv/versions/3.13.14/bin/python3 -I -S -B docs/hook-resilience-design-b/i2-probe.py
```

The probe is deliberately retained evidence rather than a new aggregate suite. It uses standard-library assertions at public process/filesystem boundaries. Every source copy, runtime destination, repository, fake executable, home and HOME/USERPROFILE/APPDATA/LOCALAPPDATA/XDG root is disposable, under a private temporary directory with paths containing spaces. No real home or source tree is hidden, moved or installed into. Git configuration is isolated. Both modes use the same canonical runtime bytes. The installed mode calls the real neutral installer, verifies every one of its thirteen delivered assets against both its manifest hash and copied source bytes, verifies the pinned interpreter, removes only its disposable copied source, then invokes the actual POSIX `scan-secrets` launcher. This proves standalone source-free installed execution without provider trees.

Both Python runs passed all following composed assertions for both source-copy and installed-launcher modes:

- No arguments, help, version and command help succeed outside a repository with safe streams. Common JSON/quiet/no-input/no-color flags produce one versioned object. Unknown abbreviations return 3 without reflecting the supplied fake credential. Check outside a repository returns 3/`not_repository`; status outside returns informational 0/`not_repository`. Missing history returns informational 0/`not_scanned`.
- A complete-clean explicit check returns 0 with required audit written. After writing a fake credential, status still returns exactly the captured historical clean result and unchanged report bytes. Every status response says `historical: true` and `authorizes_publication: false`.
- A real held report lock causes display persistence to time out. The new content finding remains exit 1/`complete_findings`, complete coverage and `security_outcome: findings`; required audit remains `written`. Status independently reports `failed`/`status_timeout`, and the prior report bytes/result remain unchanged. The next explicit check finds the credential and writes new finding history.
- Replacing the disposable audit file with a directory forces real required-audit failure. The check returns 2/`incomplete`, retains complete inspected coverage, known findings/counts and `security_outcome: findings`, and independently writes incomplete status when possible. The valid informational status still returns 0. Making its report unreadable separately returns status 2/`unavailable` without read-side repair.
- Removing every detector/acquisition helper from the disposable bundle leaves only CLI, status and neutral native filesystem helpers. The unmodified source entrypoint or installed launcher still reads the same historical report. A separate protected Python process runs that same installed/source entrypoint through an OS audit sentinel denying subprocesses, network construction/connect, write opens/mutations, repository/data enumeration and content/index/config reads. It returns the identical result with unchanged data bytes/modes/mtimes. A deliberate forbidden mkdir is rejected with sentinel exit 91 and no directory, establishing that the sentinel actually activates. This instrumented process is supplementary to the unmodified launcher proof; it does not replace the launcher or runtime in the repository.
- Check finishes while caller stdin remains open and leaves the bytes unread. Help, check and status with closed output pipes fail within five seconds without a traceback. A real pseudo-terminal supplies both stdin and stdout with its input deliberately held open; concurrent terminal draining produces one parseable, redacted, escape-free finding JSON with no prompt, under NO_COLOR/TERM=dumb. Existing installed-suite coverage separately exercises help/version/status with open stdin and PowerShell forwarding.
- At capture's real executable boundary, a private Git fixture starts in its own process group/session and launches a descendant that installs a SIGTERM-ignore handler before announcing readiness. Both inherit output pipes. SIGINT sent to the actual source process or installed launcher PID yields 130/`cancelled`; bounded `communicate()` reaches EOF, and native `ps` finds no running root or descendant (absence or a terminated zombie is accepted). Assertions run before cleanup-only kills. Cancellation is recorded as incomplete historical status when possible. No saved clean report can convert cancellation into success.

Final Python 3.14.6 observed cancellation intervals were 0.714 seconds for source and 0.643 for installed. Native ps reported both root and descendant `absent` in both modes. Final Python 3.13.14 intervals were 0.629 seconds for source and 0.618 for installed; both root and descendant were again `absent` in both modes. These intervals include the fixture readiness, cancellation, process observation and final status query; they are bounded functional observations, not performance benchmarks.

Early probe drafts failed on fixture assumptions: restoring removed files initially lost their executable modes; an outside-repository assertion initially used a nonexistent outcome label instead of the documented reason field; and cancellation initially expected the prior history rather than the required newly saved incomplete history. A first terminal harness also waited without draining its finite PTY output buffer; concurrent draining fixed that harness backpressure on both Python versions. Each was corrected from current public behavior/source without changing product code or weakening the contract. No product failure was found by the final composed proof.

## Observed verification

Commands ran serially where installation/source mutation could overlap. The CLI suite and composition probes used narrowly scoped escalation for native `ps` observation. No generator fixture mutation suite was needed because runtime/generated source is unchanged.

| Command | Actual result |
| --- | --- |
| `rtk proxy python3 -B scripts/test-scan-secrets-cli.py` | 35 passed, 16.884 seconds |
| `rtk proxy python3 -B scripts/test-scan-secrets-status.py` | 29 passed, 14.573 seconds |
| `rtk proxy python3 -B scripts/test-install-scan-secrets.py` | 21 passed, 40.656 seconds; includes both real platform installers in disposable homes and PowerShell launcher forwarding |
| `rtk proxy python3 -B scripts/test_test_all.py` | Final 14 passed, 11.417 seconds after the exact-command assertions; earlier 14 passed in 12.103 seconds |
| Both composition commands above | Passed source and installed assertions on Python 3.14.6 and 3.13.14 |
| `rtk proxy python3 -B scripts/generate-hooks.py --check` | All 62 generated outputs current |
| Public `test-all.py --list` | 56 maintained commands |
| Read-only `compile(...)` of both runner files and retained probe | Passed without pyc writes |
| `rtk proxy git diff --cached --check` | Passed for all four assigned staged files, including both new artifacts |

The whole 56-suite aggregate was not run. No existing test was deleted, weakened, disabled or skipped to obtain a pass. The maintained suites establish broader source cancellation/capture, history identity/storage races and installer behavior; the probe adds their public-process composition. Prior prerequisite evidence remains in [source audit evidence](t3b-audit-evidence.md), [status evidence](t4-evidence.md) and [installed packaging evidence](t3c-evidence.md).

Execution is macOS/POSIX, including real PowerShell on macOS where the installed suite invokes it. Native Windows kernel behavior, cancellation, ACLs, reparse races and NTFS installer execution remain **UNVERIFIED**. Generated provider delivery, authenticated host delivery, live installation, Git publication gates, Git LFS/publication, repository hook installation and provider lifecycle migration were not performed. This node does not claim milestone acceptance or authorize subsequent T5 work.

## Frozen SHA-256

| File | SHA-256 |
| --- | --- |
| `scripts/test-all.py` | `ee074dc927554649527b8b3c5819735c2e43614b4956127e475f24a7c84b449b` |
| `scripts/test_test_all.py` | `b1ceedd9208e972598e70744c89e9f418dc1c7c0622a80ca5da05881b06a7d8b` |
| `docs/hook-resilience-design-b/i2-probe.py` | `c20ce779ba30dd4369357ebe84cab0e8e5fc384daeaab20a62ad6049caa64a0c` |
| `scripts/scan-secrets.py` | `ea9f6adf225889e0ff9297d32e88e9660cea6a9d917ca87f6d95ada6d3afc497` |
| `hooks/runtime/scan_cli.py` | `0b7f492229054b3398a23f605ddf13ef06167efa9be695078c776dd98c299fa5` |
| `hooks/runtime/scan_status.py` | `bb18c76547798d33c647fcf02e78e43cb5170329be08d1e4cfcc3fc27d304753` |
| `hooks/runtime/scan_native_file.py` | `660222d89c1b01d3ef77a34920362c99d2567a11c98cdddc24db542e34a788fb` |
| `hooks/runtime/scan_audit.py` | `50973ffa051b6750173a0afe22262ffef4f34250a700839e6be5b6b132d9a0e2` |
| `scripts/install-scan-secrets.py` | `97d7edeaca305ba47edc7acb8c8d4208dee4d1ede08faf1d8d8e42fee7c07ed0` |

The final six runtime/installer hashes match the accepted prerequisite evidence. Review covered correctness, readability, architecture, security and performance: the registry follows the existing explicit pattern; the retained probe uses isolated public processes, finite watchdogs, activated fault controls and assertions before cleanup. No product or registry blocker remains. The primary independently reviewed the initial registry/composition evidence and owns final integration review. The staged whitespace check includes both newly added files.
