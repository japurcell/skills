# T1 fixture-patch preflight evidence

Status: owner-approved verification-only implementation complete, including the canonical scanner Git-session cancellation repair. The complete 20-case cleanup suite passed; two later B3 diagnostic cases and existing affected cases passed separately on the final source. Actual-repository checking and generated freshness pass. Exact runs and source identities appear below. Integration/registry/plan reconciliation remain with the primary. This document records source-only evidence on native macOS, Python 3.14.6 and Git 2.54.0. It does not establish installed provider delivery, Windows execution, live-home deployment, or publication protection. The primary agent owns the active ExecPlan and any scope decision.

The implementation is [the public preflight CLI](../../scripts/verify-security-fixture-patch.py). The [public-process acceptance suite](../../scripts/test-verify-security-fixture-patch.py) covers the owner-approved read-only process seam. The owner explicitly removed application and journaling after the concurrency finding; mutation-only product cases were removed with that feature. Check coverage and existing unrelated suites remain intact.

## Implemented check behavior

The CLI requires `--patch PATH|-`, explicit repeated `--path`, explicit `--active-hook-root`, and explicit `--check`. It has no mutation action or mutation backend. The active root contains `.codex/hooks`, `.copilot/hooks/scripts`, and `.gemini/hooks/scripts`. Candidate scanner files come independently from this source checkout. Each bundle reports its own embedded scanner build, diagnostic build and exact runtime-closure SHA-256; matching active/candidate versions are not inferred.

A private owner-only disposable repository reproduces the HEAD tree, staged entries, worktree bytes/modes and relevant untracked files. Raw objects populate its index without source configuration or hooks. Real Git applies and classifies the patch. The three real generated scanners inspect the pending state plus complete changed worktree/index views through native provider envelopes in block mode. Runtime-assembled fake controls must produce the maintained credential finding under both bundles. The tool validates fresh owner-only `scan.log` records, build, mode, scope, coverage and native permissions; process exit zero alone never authorizes the candidate. Generic `audit_init` only creates the generic audit directory; the scanner's required fsynced audit is `scan.log`.

Unsafe relative paths, linked targets/parents, special/binary targets, rename/binary patches, unresolved indexes and observed state drift reject before target mutation. Ambient scan-skip, warning and allowlist settings are removed. Child waits, patch input and retained output are bounded. POSIX cleanup first gives the scanner SIGINT so its protected Git capture can clean its separate session, then uses bounded observed-descendant cleanup when needed. Numeric process observation is a prerequisite; its failure makes verification incomplete. Windows checking currently refuses before starting subprocesses because descendant cleanup has not been verified there.

## Red/green observations before the concurrency finding

Commands were run from `/Users/adam/.codex/worktrees/design-b-t1/skills`, using `rtk proxy python3 scripts/test-apply-verified-security-fixture-patch.py` and focused `-k` selections.

- The initial moved-literal end-user reproducer failed because the CLI did not exist; the implemented CLI then rejected the moved fake credential with exit 1 and unchanged target bytes/mode/index.
- Complete changed-content coverage first failed because pending diff suppression hid a retained credential. Adding full changed-file views made that same case reject with exit 1.
- The repaired fixture test first failed because real detector controls were absent. After adding runtime controls, both source representations produced the intended fake runtime bytes and all six controls were detected. This historical observation does not establish safe application.
- An initial midway filesystem fault test used `/dev/fd` readlink, which is not portable on macOS and did not reach the intended write boundary. It was corrected to identify open files by `fstat` identity; assertions were retained. The corrected failure case showed rollback of unchanged transaction bytes and preservation of an edit observed before a later write.
- The eight-case suite at that point passed in 37.719 seconds. This was superseded by the later adversarial rename-boundary failure and must not be treated as full T1 acceptance.

No exact byte snapshot/hash was saved for that earlier unsafe implementation. Neither the worker nor the primary retained one. Historical source identity is therefore unavailable; no reconstructed file is presented as the observed version.

## Decisive noncooperating-editor race

The historical `test_concurrent_edit_at_replacement_boundary_is_never_overwritten` launched the actual CLI through `runpy` in an isolated Python process. Its only filesystem boundary substitution wrote `concurrent editor bytes` to the live target immediately before delegating to the real `os.rename`. It preserved the reported descriptor-relative capability. It did not mock the scanner, Git classification, CLI parser, or application policy.

Observed command:

```sh
rtk proxy python3 scripts/test-apply-verified-security-fixture-patch.py -k replacement_boundary
```

Historical boundary injector, with `target` bound to the disposable repository's `fixture.py`:

```python
real = os.rename

def racing(source, destination, *args, **kwargs):
    if str(destination) == "fixture.py":
        Path(target).write_bytes(b"concurrent editor bytes")
    return real(source, destination, *args, **kwargs)

os.rename = racing
os.supports_dir_fd.add(racing)
sys.argv = [str(CLI), "--patch", str(patch), "--path", "fixture.py",
            "--active-hook-root", str(ROOT), "--apply", "--json"]
runpy.run_path(str(CLI), run_name="__main__")
```

Observed result: one failure in 4.263 seconds. The expected incomplete exit was 2; the actual exit was 0 and the JSON result said `applied`. The replacement overwrote the noncooperating edit. The decisive implementation ordering was:

```python
current = os.stat(leaf, dir_fd=parent, follow_symlinks=False)
if current_identity != expected_identity:
    raise Failure("state_drift", 2, "apply")
os.rename(temporary, leaf, src_dir_fd=parent, dst_dir_fd=parent)
```

The target's advisory `flock` did not prevent a writer that ignored that lock. A final stat plus ordinary rename is not atomic compare-and-swap. [Linux flock documentation](https://man7.org/linux/man-pages/man2/flock.2.html) explicitly permits unrelated I/O to ignore advisory locks. [Rename documentation](https://man7.org/linux/man-pages/man2/renameat2.2.html) describes unconditional replacement/exchange and exclusive no-replace, not replacement conditional on an expected inode. Apple's [exclusive rename](https://developer.apple.com/documentation/foundation/urlresourcevalues/volumesupportsexclusiverenaming) and [swap rename](https://developer.apple.com/documentation/foundation/urlresourcevalues/volumesupportsswaprenaming) descriptions likewise do not establish that missing guarantee. Exchange can preserve displaced bytes, but another check/exchange recovery race still needs resolution.

The unsafe application path was first replaced with safe refusal while the original acceptance tests remained red. The owner then explicitly selected the verification-only tool. The current canonical CLI/suite were renamed to `verify-security-fixture-patch.py` and `test-verify-security-fixture-patch.py`; the mutation backend and mutation-only tests were removed as part of that authorized feature removal. The repaired runtime test now executes the verified representation in a separate disposable fixture and asserts that live bytes, modes and index remain unchanged. No atomic compare-and-swap claim remains.

## Committed HEAD capture correction

`test_failed_committed_head_capture_is_not_treated_as_unborn` substitutes a failure only at the public subprocess boundary for `git rev-parse --verify HEAD`, leaving a real committed repository and all other Git commands intact. Before the correction the CLI incorrectly returned complete-clean exit 0. After the correction, a failed HEAD probe requires both a valid symbolic branch and an independently absent ref. An existing ref makes that failure incomplete (`head_capture_failed`, exit 2). The unchanged focused case passed in 0.167 seconds.

## Further observed CLI evidence

After safe refusal and HEAD correction:

- `-k open_stdin`: passed in 6.354 seconds. Help returned with stdin still open; patch stdin timed out with a stable reason; EOF-delimited patch checking succeeded despite inherited skip/warn/allowlist settings, with six real fake-credential controls and unchanged live state.
- `-k cancellation`: passed in 0.552 seconds. SIGINT returned 130 without a traceback, terminated the sleeping scanner's descendant process group, and preserved live bytes/mode/index.

The finalized renamed suite first completed 15 functional cases in 43.196 seconds with one infrastructure error: the default sandbox denied `ps` during the cancellation assertion. This is not a failing product decision or successful cancellation proof. The same process-inspection requirement was then exercised with scoped escalation.

A further public reproducer found that a same-size dirty file could cause source `git status` to execute a configured clean filter. The retained `test_source_filter_commands_are_never_executed` first failed because its harmless temporary filter ran. Removing the unnecessary source status call fixed it; index/object/worktree fingerprints provide the captured state directly. The focused case passed in 4.043 seconds.

Final command: `rtk proxy python3 scripts/test-verify-security-fixture-patch.py`. Observed: all 16 tests passed in 46.475 seconds under scoped escalation for process inspection. This includes broken stdout pipes, open/EOF patch stdin, invalid/abbreviated options, quiet JSON, redaction, cancellation, unresolved indexes, binary/rename inputs, special/linked targets, dirty staged and untracked credentials, source-filter isolation, independent active build identity, and complete-file detection.

The earlier 16-case source snapshot identities were:

- `scripts/verify-security-fixture-patch.py`: `fab60ac0066ba200726cd1ecfedae28306550745a014129dc5f22a297f8a7a70`
- `scripts/test-verify-security-fixture-patch.py`: `18ef2af4970caf30c654c920cd1d420358d90b76113ad4f923084371b85d4455`

Platform: macOS 26.7.1, Python 3.14.6, `/usr/bin/git` 2.54.0 (Apple Git-157). Base revision: `074ca4fa`. Tested generated scanner policy build: `471533ef86089e4b`; active and candidate runtime closure hashes are independently returned by successful CLI JSON. The separate active-copy case deliberately changes one reviewed script's bytes and proves its runtime-closure identity differs from the candidate.

No test process ran during a granted D0 quiet window.

## Ownership and remaining work

Only the CLI, its suite and this evidence document belong to this task. No generated hooks, manifest, installer, provider template, registry, active ExecPlan or canonical KB was edited. The primary performs registry integration and one coordinated KB pass. No real-home installation, hook enablement/trust change or publishing occurred. These three files form the scoped private T1 commit; its hash is returned in the worker delivery and remains available through Git history.

The owner-approved T1 outcome is verified read-only preflight. The primary must reconcile the active ExecPlan, dependencies and suite registry with this explicit scope change. The complete renamed suite, generated freshness and staged whitespace verification pass as recorded below. Native Windows checking remains unsupported until bounded descendant cleanup is verified. No automatic fallback writes or bypass flag exists.

## Final consistency, byte fidelity and practical workload proof

Three public faulty-adapter controls first reproduced result inconsistencies: a purported clean record carrying findings/truncation/omissions incorrectly verified with exit 0; findings without native denial and findings with unsafe audit mode incorrectly returned exit 1. The verifier now validates fresh owner-only single-record audit, complete coverage, status/findings consistency and native permission before assigning complete-findings or complete-clean. The unchanged focused test passed in 2.006 seconds. Those faults return incomplete exit 2.

The first actual-worktree invocation used a harmless docstring patch targeting this CLI, with the current checkout explicitly selected as the reviewed active root. The repository baseline contained 3,314 tracked paths and 56,370,061 working bytes; this worktree also contained the three pending T1 additions. The frozen 17-case implementation reached its unchanged 180-second total limit: elapsed 180.356 seconds, exit 2, reason `operation_time_limit`, stdout remained one safe JSON object, stderr was empty, and target bytes/mode plus raw index SHA-256 were unchanged. Source fingerprint: `658d23bf82bd7cc59c7592b4f6cb28b5df847752c87d4c53e30a5ae4ea771e5f`. The failure was retained before optimization.

Measured per-file process overhead justified batching. The current implementation checks immutable object IDs/types/sizes through bounded `cat-file --batch-check`, acquires complete framed blobs through bounded `--batch` chunks, rejects header/size/trailer disagreement, builds raw HEAD objects/tree with `fast-import`, and installs staged versions through one NUL-delimited `update-index --index-info` stream. Distinct immutable object bytes remain bounded at 128 MiB; worktree state remains 64 MiB/4,096 paths, patch input 1 MiB, each child 12 seconds and the total operation 180 seconds. No bound was increased to pass the workload.

The public tracked-attribute fixture stores a raw CRLF HEAD/index blob alongside tracked text attributes. The reviewed active adapter observes the actual pending repository's HEAD bytes, and the test checks exact CRLF preservation and unchanged live/index fingerprints. The focused case passed in 4.115 seconds. Source configuration and tracked attributes never normalize the captured baseline during raw object/index construction.

Initial delivery suite: `rtk proxy python3 scripts/test-verify-security-fixture-patch.py` passed all 18 cases in 52.130 seconds. Generated freshness: `rtk proxy python3 scripts/generate-hooks.py --check` reported `Generated hooks are current (38 files).` Staged whitespace: `rtk git diff --cached --check` passed.

The same harmless actual-worktree check then passed in 7.846 seconds, exit 0, six real credential controls, no stderr, and unchanged target/index fingerprints. Its public invocation was:

```sh
rtk proxy python3 -I -S -B scripts/verify-security-fixture-patch.py --patch /private/tmp/design-b-t1-realistic.patch --path scripts/verify-security-fixture-patch.py --active-hook-root /Users/adam/.codex/worktrees/design-b-t1/skills --check --json --no-input
```

This establishes practical source verification at the observed footprint; it is not a general latency benchmark or native provider-delivery claim. Both outcome records were retained separately in private temporary artifacts during execution and their decisive measurements are captured here.

Initial delivery source SHA-256 (private commit `73f48e5cc0e74df87a5285cfa813365f17787d72`):

- `scripts/verify-security-fixture-patch.py`: `0640d17d3a2dd285fd16970ce0d3959a906bb669a6b008724501a4986fddcdde`
- `scripts/test-verify-security-fixture-patch.py`: `d1ee439940d539ec1422cfac479c7e5eb96488389bec34a7bf974acbb0363106`


## Canonical protected-capture cancellation repair

Primary review identified a process class absent from the initial inherited-group cancellation fixture: the maintained scanner's `capture_git` launches Git with `start_new_session=True`. Immediately killing only the scanner's group can prevent its `finally` cleanup and leave that Git session alive.

The retained public test `test_cancellation_cleans_real_scanner_capture_git_session` copies the real generated scanner and leaves its protected-capture implementation intact. At module entry it selects a harmless temporary Git executable that records numeric PID, parent, group and session metadata before sleeping. The observed Git PID equals its group and session IDs, and differs from the parent scanner's group. Two subcases use a responsive scanner and a scanner that ignores SIGINT. Each cancels the actual public verifier while that canonical capture is waiting, requires exit 130 and stable JSON without traceback, requires bounded completion, and checks that the recorded Git child is gone or a zombie before fixture cleanup. The fixture's final cleanup cannot turn a surviving child into a pass.

Red against the exact initial delivery source `0640d17d3a2dd285fd16970ce0d3959a906bb669a6b008724501a4986fddcdde`: both subcases failed in 1.706 seconds, with surviving Git process status `Ss`. Unlike the earlier unsafe application snapshot, this source identity is retained exactly in commit `73f48e5cc0e74df87a5285cfa813365f17787d72`.

The repair records cancellation intent without interrupting child PID ownership assignment. It observes bounded PID/parent/group/start-time/state metadata through absolute `/bin/ps`, retains observed ancestry through reparenting, and matches recorded identities before signaling. Cleanup gives the scanner SIGINT first so canonical `capture_git` can run its own cleanup. A bounded grace period is followed by forced signaling and fresh observation of the recorded descendants and their groups. A redundant group-signal race initially surfaced as `PermissionError`; fresh observed liveness now decides whether cleanup succeeded. Root reaping and observation termination have reserved headroom within the two-second cleanup allowance. No command arguments, source paths, child stderr, or fixture bytes enter process metadata diagnostics.

Process observation is limited to 1 MiB and 0.25 seconds per snapshot; cleanup retains at most 256 observed processes. Failure to access numeric process metadata refuses before Git/scanner launch. The public observer-failure case proved no Git launch and unchanged live fingerprints. Windows continues to refuse before launch. This is evidence for the maintained scanner's separate Git-session behavior, including a scanner unresponsive to SIGINT; it does not establish containment of arbitrary malicious daemonization or unobservable processes. Observation/cleanup failure remains incomplete.

Focused green: both cancellation methods passed in 6.178 seconds; the canonical session test alone passed in 4.609 seconds. The complete command `rtk proxy python3 scripts/test-verify-security-fixture-patch.py` then passed all 20 cases in 86.576 seconds, with scoped process-inspection permission. That full-run snapshot had source SHA-256 `3f39cbb6e02887b92c5b9edf19bf2e90c06154c27c45b038383e76db7a8dc3ee` and suite SHA-256 `8706e444927a5f9dcecf4e2d86365fdbe705e18bc71c6c51c157cf2cb11728b7`.

## Final B3 diagnostics and frozen workload proof

Two additional public cases reproduced missing safe resource measurements and a misleading generic Git-availability repair action. The resource case initially failed all three subcases: a 1,048,577-byte patch against a 1,048,576-byte limit, 65 targets against a 64-path limit, and controlled child stderr exceeding its 1,048,576-byte limit. The missing-Git case reproduced the generic action. The final implementation returns safe measured/limit/unit values where known, static reason-specific repair text for Git/process/platform/resource failures, and no raw stderr, paths or argument echoes. Runtime fake credential bytes in oversized input/output remain redacted. These changes retain all existing resource bounds.

Focused final-source results: resource measurements passed in 0.301 seconds, missing Git in 0.126 seconds, observer prerequisite in 0.113 seconds, and existing help/version in 0.471 seconds. The suite now contains 22 cases. The complete 20-case algorithm suite above and these focused final-source cases are the evidence; no aggregate 22-case pass is claimed. No broad rerun was performed solely for diagnostic wording.

The final frozen actual-repository invocation used the same harmless docstring patch and public command recorded above. It completed in 10.360 seconds, exit 0, with six real credential controls and empty stderr. Target bytes/mode and raw index SHA-256 remained unchanged. Source mode was 0755; raw index SHA-256 was `039854f2948b21238ccbcab5b1fbb192d9300ccdefa1ab1c531e0e8e13acad1b`. Its separate private result artifact was `/private/tmp/design-b-t1-realistic-cleanup-repair-result.json`; prior failed and successful workload artifacts were preserved. Generated freshness again reported `Generated hooks are current (38 files).`

Final repair source identities:

- `scripts/verify-security-fixture-patch.py`: `07da7b8a321104f4e2b525bade6e62a21fb5f577074915a798aa418517abbc06`
- `scripts/test-verify-security-fixture-patch.py`: `06a48f6da41c86948e1b68ee0665f8e8644a47128afb9a3ffa830057381b53e5`

The repair remains private, source-only and verification-only. Initial delivery history is preserved; shared files, generated scanner sources and installed hooks remain outside this task's changes.
