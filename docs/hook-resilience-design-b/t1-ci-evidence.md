# Hosted fixture-preflight observation repair

Status: T1-CI scoped acceptance is met. The final bounded repair passes all 28 public preflight methods on actual hosted Python 3.13.16 arm64 and fresh local Python 3.14.6. The complete macOS workflow still fails a later, separately owned Codex scanner assertion; this task does not accept that workflow or native Windows behavior. The primary owns the active ExecPlan, reviewed candidate transport, integration and final coordinated KB pass. This task owns only this evidence file and the two fixture-preflight scripts. No private worker branch is published.

## Observed hosted red

The actual [macOS run 38978729981](https://github.com/japurcell/skills/actions/runs/38978729981/job/117234305798), source `d8d58e0814f7c3e1ef4fe766db555eef1bd3aa79`, failed the maintained preflight command `rtk proxy python3 scripts/test-verify-security-fixture-patch.py`. The suite ran 26 methods in 179.922 seconds. Only `test_open_stdin_is_bounded_and_help_does_not_read_it` failed: a valid explicit patch expected exit 0 and received exit 2 with `process_observation_timeout`, phase `cleanup`, allowance 0.25 seconds, measured 0.298 seconds. Setup, native-tool verification and generated freshness passed; later recovery/reporting/scanner steps were skipped after that failure.

The runner used Python 3.13.16 arm64 and Homebrew Bash. Its disposable HOME, USERPROFILE, CODEX_HOME, TMPDIR and XDG roots contained spaces. The log and run metadata were inspected with read-only `gh run view` requests. The separate actual Windows run `38978729929` failed its installer baseline and is outside this repair.

Private source started from `fcaacc74` on `codex/design-b-t1-ci`. Both owned scripts at that starting revision exactly matched the failing hosted source, verified by `git diff d8d58e0814f7c3e1ef4fe766db555eef1bd3aa79 HEAD -- scripts/verify-security-fixture-patch.py scripts/test-verify-security-fixture-patch.py` producing no diff.

## Cause and bounded repair

Every managed Git/scanner child is followed by full-host metadata observations, including cleanup after ordinary successful child exit. The absolute `/bin/ps` command enumerates PID, parent PID, process group, start time and state. Its regular-file output and parser remain limited to 1 MiB; command text is never requested. The old 0.25-second wait can expire on an ordinary hosted observation. The log establishes this symptom, not a claim about the runner's exact scheduler load or kernel implementation.

A 0.5-second allowance leaves about 0.2 seconds above the observed hosted 0.298-second case while preserving finite observation. The old `PROCESS_SECONDS` also reserved twice its value inside cleanup. Raising it without separating those roles would reduce useful cleanup time and could strand a resistant separate-session child. The repair allocates at most 0.5 seconds per observation, including process creation, and separately at most 0.1 seconds to stop/reap an observer. Cleanup uses one absolute two-second deadline, clips each observation to its remaining time, and reserves a full observation and both reaps before forced termination. It enters forced termination before another graceful observation would consume that reservation. Final leader reaping uses the remaining cleanup allowance. Ordinary observations also honor the invocation's remaining deadline.

The overall 180-second invocation, 12-second child, two-second stdin and two-second cleanup contracts remain unchanged. PID/group/start identity checks, retained ancestry, the 256 observed-process limit, exact independent fake-credential controls, read-only live targets/index, strict incomplete outcomes and cancellation semantics remain in place. There is no automatic scanner retry, fail-open handling or environment override. Help and actionable recovery now state the revised observer allocation.

## Test-first public process proof

The two additional test methods launch the maintained CLI as a real process. A disposable launcher substitutes only the OS observer process boundary: a short isolated Python process sleeps and then `exec`s the exact real `/bin/ps` command. It does not replace the verifier's internal functions, its parser, Git, scanners, status schema or cleanup implementation. Recorded observer PIDs are checked after the CLI exits. Tests never emit command text, source content or credential bytes.

Before the product edit, meaningful native execution of these two methods took 2.599 seconds and failed both: a 0.3-second real observer delay returned exit 2 instead of successful verification, reporting allowance 0.25 and elapsed 0.253 seconds; cancellation with a resistant separate-session child returned exit 2 instead of 130, reporting elapsed 0.260 seconds. A 60-second stalled observer remained bounded at 0.312997 seconds and was stopped. An earlier sandbox-only trial could not execute `/bin/ps`; it is an environment failure, not native red evidence.

After the repair, the two-method focused run passed in 12.207 seconds on macOS 26.7.1 arm64/Python 3.14.6/Git 2.54.0. The valid patch with its first two observations delayed 0.3 seconds verified in 8.151730 seconds with all six independent controls; 145 recorded observer processes had stopped. A stalled 60-second observer returned incomplete in 0.547279 seconds before any Git launch; its observer had stopped. Cancellation after the real scanner created a resistant child in a separate process session returned exit 130 and `interrupted` in 1.530013 seconds. All 52 recorded child/observer processes were stopped or non-running zombies before fixture cleanup, and the live target/mode/index/status fingerprint matched. Final fixture kills occur only after the leak assertions, so they cannot make a leak pass.

All original 26 test methods and assertions are retained. The added POSIX-only tests do not establish Windows support; the public CLI still refuses native Windows checking before child launch.

## Composition for current hosted proof

Before the first hosted repair invocation, primary required a clean private rebase onto accepted T8b base `7f6166543bb39071e0533e95b9fc5363e52549e0`. It completed without conflict. The original frozen candidate `371aad3155a1e9afa34f7795f611da533669ee00`, tree `2224d6244de21ca195ff63e63c27973bf1e540bc`, and its original receipt/33-input manifest are preserved under `/private/tmp/design-b-t1-ci/` with `.before-composition` suffixes. The owned CLI and test bytes/modes are unchanged by composition.

Comparison of all 33 scanner/helper fingerprints found exactly three changed provider scanner files and 30 unchanged helpers. This is broader than a diagnostic-build constant change: for every scanner, the changed top-level AST nodes are precisely `SECURITY_HOOK_FILES`, `_diag_registrations`, `DIAG_BUILD`, `DIAG_REGISTRATIONS` and `REPORT_BUILD`. The trusted security-script names now include `scan-status.py`; the diagnostic function validates and excludes Gemini's disabled-name list; registration/build metadata follows accepted T8b. All other top-level AST nodes compare exactly equal with source locations excluded. No constant-only equivalence is claimed. The read-only static receipt is `/private/tmp/design-b-t1-ci/composition-static-receipt.json`.

| Changed current input | SHA-256 | POSIX mode |
| --- | --- | --- |
| `.codex/hooks/scan-secrets.py` | `7528cece30be86579788aeda6c0d710509aa547426f3dbedba10cee9de10e8a5` | 0755 |
| `.copilot/hooks/scripts/scan-secrets.py` | `a8e1dcc8132b61067964851c82d8cfc5f3eae71886ef9dece64472de73ac1cdb` | 0755 |
| `.gemini/hooks/scripts/scan-secrets.py` | `e25defb542d2b118540c02cf81adb5f9050d4744d346e7f2f5f94aab18e76821` | 0755 |

The current 33-input manifest SHA-256 is `c7d8496a7d91231659290ea40cd88954e22dfa3ba1d69a5411ae672d7a685d21`. The earlier local full suites establish only their original tree. The first composed candidate was transported exactly as snapshot `c2d37b5921b3f80ee28d6f558026f33dc46ecc41`, tree `3f27b0e915159a09efbab7f10fde837fa5dc9b3a`. Its complete fresh local Python 3.14 suite passed 28 methods in 151.238 seconds (wall 151.279207) with spaced disposable roots; all 35 recorded source inputs and modes matched before/after and the worktree remained clean. Log: `/private/tmp/design-b-t1-ci/suite-python314-composed-spaced-roots.log`; receipt: `composed-python314-receipt.json.before-reap-repair` in that directory. The delayed valid CLI took 8.216451 seconds with 146 stopped observers; stalled observer took 0.555025 seconds with one stopped observer. This local pass did not accept the hosted result.

## Second actual hosted red and leader-reaping repair

Actual [macOS run 38980691223](https://github.com/japurcell/skills/actions/runs/38980691223), source snapshot `c2d37b5921b3f80ee28d6f558026f33dc46ecc41`, failed the full 28-method suite after 198.153 seconds. Only the new resistant separate-session cancellation method failed: expected exit 130, received incomplete exit 2 with `process_observation_timeout`, clipped allowance 0.316 seconds and measured 0.341 seconds. Its ordinary 0.3-second delayed real observer control passed in 12.683046 seconds with 189 stopped observers; its 60-second stalled observer control passed in 0.605689 seconds with one stopped observer. The original open-stdin case passed. Later workflow steps did not run after this preflight failure. This red remains retained evidence, not a passing run or a reason to change the two-second cleanup requirement.

Static tracing identified a concrete stale-state check in both cleanup loops: the leader is polled before the potentially slow metadata observation, then its pre-observation return code is tested afterward. A leader killed immediately before collection can finish during that observation, while the stored return code remains `None`. Even with no living descendants in the fresh snapshot, that stale value requires another observation with less remaining time. This explains a possible unnecessary clipped final observation; the exact scheduling of the failed host was not directly traced.

The second repair polls the managed leader again after each successful cleanup observation, immediately before deciding whether cleanup is complete. Fresh descendant identity checks are unchanged, and successful cleanup still requires both a reaped leader and no living verified descendants. This changes neither the 0.5-second observation allocation nor any overall deadline. It introduces no retry and changes no test, assertion or fault delay. The actual hosted failure above is the test-first red for this minimal additional repair. Previous local passes apply to the earlier candidate; the final repair received the fresh local Python 3.14 and actual hosted full-suite proof recorded below. The old candidate/input receipts are preserved with `.before-reap-repair` suffixes.

All local execution of the earlier candidate drained before this edit. I4 ran its isolated probe while the second repair was prepared; primary then handed the exclusive local window back for exactly the two focused methods and full suite. Those groups ran serially and drained before the window was released. Primary owns exact tracked-tree transport and run collection. Both source files stayed frozen throughout the hosted invocation; final changes after its result are evidence and commit-message updates only.

## Final scoped acceptance

The final private executable candidate was `df71cc76af9a5f80394b3402b9fb74ffb7f39123`, complete tracked tree `eb11616982fd92b4981ffeabb9899d4b4b5fcfc9`. Primary independently verified the three owned file hashes/modes and all 33 scanner/helper inputs, then published that exact tree as snapshot `a7dcc027327b2476a2377bcf8c50c96e4c2dd387`.

Actual [macOS run 38981378635, job 117242777153](https://github.com/japurcell/skills/actions/runs/38981378635/job/117242777153) passed `Test verification-only fixture preflight`. The finished job log directly records Python 3.13.16 arm64, Homebrew Bash and disposable HOME/USERPROFILE/CODEX_HOME/TMPDIR/XDG roots containing spaces. It reports `Ran 28 tests in 203.369s` and `OK`. Step metadata spans 2026-10-16 23:26:14 through 23:29:38 UTC, or 204 seconds at whole-second precision; that wall interval is separate from the unittest duration.

| Final proof | Methods / unittest duration | Delayed ordinary real observer: valid CLI seconds / stopped observers | Stalled observer seconds / stopped observers | Resistant separate-session cancellation seconds / stopped child and observers |
| --- | --- | --- | --- | --- |
| Local Python 3.14.6 focused methods | 2 / 11.577 seconds | 7.898099 / 143 | 0.557521 / 1 | 1.146402 / 51 |
| Local Python 3.14.6 full suite, spaced roots | 28 / 149.568 seconds | 8.123272 / 142 | 0.560997 / 1 | 1.141265 / 51 |
| Actual hosted Python 3.13.16 arm64 full suite, spaced roots | 28 / 203.369 seconds | 11.498893 / 189 | 0.589318 / 1 | 1.756276 / 53 |

Every final run retained the 0.3-second real-observer delay and 60-second stalled-observer fault. All original 26 methods and both new methods passed. Successful valid patches required all six real independent fake-credential controls; incomplete and canceled outcomes retained their exact statuses. Live target bytes/modes, raw index bytes and Git status fingerprints were unchanged. Child/observer leak checks occurred before fixture cleanup, and resistant cancellation retained its strict less-than-two-second assertion. The local final full-suite receipt verifies all 35 source-input SHA-256/mode pairs identical before/after and a clean worktree. No test assertion, test timeout or fault injection was weakened to obtain green.

Final local logs are `/private/tmp/design-b-t1-ci/focused-reap-python314.log` and `/private/tmp/design-b-t1-ci/suite-reap-python314-spaced-roots.log`; the complete before/after receipt is `reap-python314-receipt.json` in that directory. Hosted full-job log and exact run/step metadata are `hosted-38981378635-job.log` and `hosted-38981378635-metadata.json` there. Relevant executable inputs still match the table below and the current 33-input manifest. Only this evidence file and commit description change after that frozen proof; the final private commit/tree receipt is supplied separately to primary.

The full macOS job concluded failure after preflight success. Setup/native tools, generated freshness, diagnostic recovery and security reporting also passed. `Test Codex scanner and capture` failed immediately with an assertion at `<stdin>` line 9. Primary owns that separately scoped T8b-R stale-registration repair; this task changes none of those scanner assertions or registrations. Copilot/Gemini scanner steps and required native Darwin capture evidence were skipped afterward. Therefore this receipt establishes hosted preflight success only, not complete workflow, all-provider scanner, authenticated delivery or final Design B acceptance. Native Windows checking remains unsupported by this CLI and the separate Windows installer baseline remains W0's responsibility.

## Frozen input and validation receipt

Both owned Python files compile without writing bytecode; `git diff --check` passes. The maintained suite is already registered and wired into macOS CI, so no registry, generator, installer or workflow change belongs to this repair. No generation or installation was run.

| Input | SHA-256 | POSIX mode |
| --- | --- | --- |
| `scripts/verify-security-fixture-patch.py` | `a16ec49091099f7fae55dd58d8ad6c50985c364ebcda463745fa3c3af78e71c2` | 0755 |
| `scripts/test-verify-security-fixture-patch.py` | `d8f7486a3f751517bb29826647d1ddd4db51b60f113e78c9e8346283acbae5d6` | 0755 |

The original candidate's frozen full local suites passed serially. Exact commands used the listed absolute interpreter followed by `scripts/test-verify-security-fixture-patch.py -v`, from `/Users/adam/.codex/worktrees/design-b-t1-ci/skills`.

| Interpreter | Complete suite | Delayed real observer: valid CLI seconds / stopped observers | Stalled observer seconds / stopped observers | Resistant separate-session cancellation seconds / stopped child and observers |
| --- | --- | --- | --- | --- |
| `/Users/adam/.pyenv/versions/3.13.14/bin/python3` | 28 methods, 149.714 seconds, exit 0 | 8.027975 / 142 | 0.539152 / 1 | 1.533564 / 52 |
| `/Users/adam/.pyenv/versions/3.14.6/bin/python3` | 28 methods, 152.604 seconds, exit 0 | 8.186152 / 149 | 0.558756 / 1 | 1.532391 / 52 |

The second run created disposable HOME, USERPROFILE, CODEX_HOME, TMPDIR and XDG config/data/cache under `/private/tmp/design-b-t1-ci/hosted roots with spaces/`, matching the hosted path property. Full logs are `/private/tmp/design-b-t1-ci/suite-python313.log` and `/private/tmp/design-b-t1-ci/suite-python314-spaced-roots.log`. All original 26 methods passed, including actual open stdin, broken output, unchanged live fingerprints, independent historical active bundles, malformed scanner responses, output limits and responsive/unresponsive canonical Git-session cancellation. Every launched suite session completed before the local functional window was released; no generator, installer or other local functional suite overlapped.

The original 33 provider scanner/helper inputs used by those local fixtures are recorded with SHA-256 and POSIX mode in `/private/tmp/design-b-t1-ci/scanner-inputs.sha256-mode.before-composition`; that manifest hashes to `2eea269c2c543b4398ecebf86bf715c02db5a6e0d540d1e913b80905c9d91662`. The current composed manifest is `/private/tmp/design-b-t1-ci/scanner-inputs.sha256-mode`, identified above. The candidate's complete tracked tree is supplied to the primary after commit for exact hosted transport. Independent review must preserve these input identities or rerun affected proof.

Self-review covered correctness, readability, architecture, security and performance. The repair keeps the same fixed observer executable/metadata, scanner policy, generated assets and test seams; it adds no dependency, command override, scan retry or live-home write. Existing assertions were not changed. No orphaned code was introduced. The primary retains independent review and the one coordinated end-of-session `update-agent-docs` pass; this task supplies no new KB entry.

Actual hosted preflight green, snapshot/source/tree identities and the later independent workflow failure are recorded above. The complete workflow remains unaccepted pending its separate repair; one hosted pass does not prove an unconditional latency guarantee for every host. The original two-second cleanup bound is an ordinary local OS/process contract, not a hard real-time guarantee for stalled kernel operations or process creation.
