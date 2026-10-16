# T8a-C ordinary status cancellation evidence

Recorded 2026-10-16 in `/Users/adam/.codex/worktrees/design-b-t8a-c/skills`, branch `codex/design-b-t8a-c`, starting from `08c472eaf702b6863baaaaf3134b8346a52e9102`. This is bounded generated-process POSIX source proof. It does not establish authenticated provider delivery, native Windows containment, cancellation before the Python handler is installed, or cleanup after uncatchable adapter SIGKILL. The primary retains integration, the active ExecPlan, and the single coordinated end-of-session knowledge pass.

## Observed defect and repair

The first public regression command was `rtk proxy python3 scripts/test-scan-status-cancellation.py`. Before changing production code, its initial one-method shape (`test_sigterm_cleans_hanging_status_tree`) invoked the three real generated adapters using the same interpreter with `-I -S -B`, disposable HOME and fixed `~/.local/lib/scan-secrets/scripts/scan-secrets.py`. The controlled status CLI started a sleeping descendant, wrote its root PID, descendant PID and process-group identity, and then slept. After verifying root PID equals group ID and both PIDs belong to that group, the test sent SIGTERM to the adapter only.

All three red subcases failed: adapter exit `-15`, root state `Ss`, descendant state `S`. Whole callback observations were Codex `0.042406`, Copilot `0.040681`, Gemini `0.042391` seconds. The test's `finally` explicitly killed only each marker-identified private fixture group and reaped the adapter, including on red. The initial renderer SHA-256 was `bbfaa874ae4ada710300387376325fbe352a9cf87493656fb6229c83ecabeb5b`; the Codex adapter SHA-256 was `92bbf7c68519d0495f46bd674df0ca2d99e105bba5ef50c081ac6858db9367f3`. The primary independently observed the same public defect at 22:17 UTC and retained `/tmp/design-b-status-sigterm-red.json`; this task's red above additionally exercised all three adapters and descendants.

The canonical renderer now installs POSIX SIGTERM/SIGINT handlers that only set a cancellation flag. Input and child waits observe that flag and unwind into the existing unconditional group cleanup. Avoiding an asynchronously raised exception keeps the Popen-assignment and cleanup intervals intact. Cancellation returns the existing unavailable, historical-only informational response with exit zero where stdout remains open. Closed stdout still exits quietly. The fixed same-interpreter isolated status command, process-group containment, 64 KiB input/output caps, bounded temporary regular-file capture, ordinary callback deadlines and read-only status semantics remain intact. No scanner, Git operation, SQLite path, arbitrary environment command, checkpoint or background process was added.

The primary reviewed the change across correctness, readability, architecture, security and performance. The non-raising handler rationale matches [Python's signal exception guidance](https://docs.python.org/3.13/library/signal.html#note-on-signal-handlers-and-exceptions). The mutable-buffer input handshake follows [fcntl.ioctl](https://docs.python.org/3.13/library/fcntl.html#fcntl.ioctl). These are Python 3.13-series documentation references, independently checked by the primary, not execution on the documentation site's current patch release.

## Focused public controls

The final suite contains five methods and 21 callbacks per interpreter. It checks SIGTERM and SIGINT with hanging root/descendant processes, both signals with a closed output consumer, both signals after incomplete input has actually been consumed, and ordinary completion after the root exits while a descendant retains its inherited output handle. The latter completes too quickly to synchronize an additional cancellation after root exit; its separate public control verifies group cleanup before the informational response. Existing lifecycle fault coverage also retains that finished-root case.

Input cancellation uses a pipe containing one incomplete JSON byte before launching the adapter. The parent retains the read endpoint, confirms unread count starts at one, then waits until it becomes zero while the adapter remains alive. It sends the signal only after this public consumption handshake. A first harness attempt queried the write endpoint, which reported zero prematurely and signaled during interpreter startup: six fixture failures with adapter exit `-15`/`-2`, before a status child existed. The corrected read-endpoint handshake produced the intended input-wait proof without a product change or weakened assertion. No sleep-based startup guess is used. The pending incomplete input never starts the controlled status CLI.

All finished green fixture root/descendant observations were absent PIDs (empty `ps stat` output). Assertions permit a killed orphan temporarily remaining a zombie, but reject every running state. Callback seconds measure launch through process communication; tree checks query exact owned PIDs afterward. The printed `cancel_seconds` includes communication plus those later `ps` checks, so it is not a pure cancellation-latency measurement. No p95, global performance, throughput, provider-host or platform-wide bound is claimed.

## Commands and results

All shell invocations used `login:false` and RTK. Mutating private-worktree/test operations used scoped sandbox approval. Functional tests, generator execution and timing observations were serialized; T8b's tests stayed paused. Python 3.14.6 resolved to `/Users/adam/.pyenv/versions/3.14.6/bin/python3`; the second interpreter was `/Users/adam/.pyenv/versions/3.13.14/bin/python3`.

The commands below ran from the task worktree. Each `python3` command in the table also ran with `/Users/adam/.pyenv/versions/3.13.14/bin/python3`; no functional groups overlapped.

| Command | Python 3.14.6 observation | Python 3.13.14 observation |
| --- | --- | --- |
| `rtk proxy python3 scripts/test-scan-status-cancellation.py` | 5 methods, 21 callbacks, pass; 1.850 s suite | 5 methods, 21 callbacks, pass; 1.805 s suite |
| Selected lifecycle command below | 5 methods, 57 measured callbacks, pass; 12.005 s | 5 methods, 57 measured callbacks, pass; 11.748 s |
| `rtk proxy python3 scripts/test-generate-hooks.py` | 26 tests pass; 18.195 s | 26 tests pass; 16.639 s |
| `rtk proxy python3 scripts/test_test_all.py` | 14 tests pass; 13.225 s | 14 tests pass; 12.883 s |
| `rtk proxy python3 scripts/generate-hooks.py --check` | 65 files current | 65 files current |

```sh
rtk proxy python3 scripts/test-scan-secrets-lifecycle.py LifecycleTests.test_saved_absent_stale_incomplete_and_corrupt_history_is_informational LifecycleTests.test_open_and_malformed_input_finishes_within_outer_deadline LifecycleTests.test_child_faults_are_bounded_redacted_and_descendants_are_cleaned LifecycleTests.test_closed_output_consumer_finishes_quietly_after_cleanup LifecycleTests.test_malformed_copilot_input_is_one_portable_json_document
rtk proxy /Users/adam/.pyenv/versions/3.13.14/bin/python3 scripts/test-scan-secrets-lifecycle.py LifecycleTests.test_saved_absent_stale_incomplete_and_corrupt_history_is_informational LifecycleTests.test_open_and_malformed_input_finishes_within_outer_deadline LifecycleTests.test_child_faults_are_bounded_redacted_and_descendants_are_cleaned LifecycleTests.test_closed_output_consumer_finishes_quietly_after_cleanup LifecycleTests.test_malformed_copilot_input_is_one_portable_json_document
```

The new suite's maximum whole callback was `0.168593` seconds on 3.14 and `0.169452` on 3.13, both during incomplete-input cancellation. Hanging-tree cancellation with output open or closed observed whole callback maxima `0.071934` and `0.068892` seconds respectively. Every final adapter returned zero, with empty stderr. Open output preserved provider informational JSON; Copilot CLI-shaped input retained its progress row followed by one final `{}`, and incomplete/unknown input retained one portable final JSON object. The selected existing lifecycle observations reached maxima `0.749123` and `0.746763` seconds respectively. These are selected five-method observations, not a new full 14-method lifecycle result.

`rtk proxy python3 scripts/generate-hooks.py --write` refreshed the three status outputs. It also changed exactly the DIAG_BUILD constant in each generated scanner/diagnostic output, six mechanical lines total, because the canonical status renderer participates in those diagnostic build fingerprints. The primary verified that limited diff and explicitly expanded ownership to retain it. Final generated diagnostic identities:

- Codex: `a313eff1bc12df4d53d490026ba6ee63443569740abb4422f9737fcaa7f5e164`.
- Copilot: `90fbdf7a4af7aedfbf9e289925fe94fb47e513bca8a5ca19c1232c0d9706f96c`.
- Gemini: `92e02457e531299dbaeca1c7863a136558f1d32c6c637bdebb57ed3121430228`.

`rtk proxy python3 scripts/test-all.py --list` returned 61 commands with the focused cancellation suite registered. The public runner tests independently verify exact maintained-suite coverage and count. `rtk git diff --check` passed. Generator checks ran before final functional validation and after both generator/runner groups.

## Frozen source identities and unchanged runtime

The following SHA-256 and POSIX modes identify the final product/test bytes used by the recorded final groups. The existing lifecycle test file is included to identify selected-test scope and was not modified by this task. The evidence file's digest is reported separately to avoid a self-reference.

| File | SHA-256 | Mode |
| --- | --- | --- |
| `hooks/families/scan_status.py` | `c62d7b96fed9fef2fa3a406de73d77008de63ed3e34d86fb406f80f61a0eab25` | `0644` |
| `.codex/hooks/scan-status.py` | `126de1936d82b294e15306d99ab1a35e312d9d55e239c5941d6266ef96cf84f3` | `0755` |
| `.copilot/hooks/scripts/scan-status.py` | `b85e4efd4d159746f0ff37b3c2800638a5d39173fa3031aa104e87f0677635da` | `0755` |
| `.gemini/hooks/scripts/scan-status.py` | `0fc85f1e234497eca04264bbaa0a7bf2008fe6c3c6cf26ad910558324fb16251` | `0755` |
| `.codex/hooks/hooks-diagnostics.py` | `ca2f7183a6f974e3560058faa8a771875c208fcf982be75e5b03c8ec794292c9` | `0755` |
| `.copilot/hooks/scripts/hooks-diagnostics.py` | `0c69bc9e2b6490c2a32d49da91fa60f10396b771aac13966faad84266bfe078a` | `0755` |
| `.gemini/hooks/scripts/hooks-diagnostics.py` | `ba10618a5d2b91786960fd725e08fe1d9bec8f221669c15e87697dbae8ecfd2a` | `0755` |
| `.codex/hooks/scan-secrets.py` | `5219a60511506553910d80ff3a09e5bb8c7af552b52228eae666d8a14f62c12e` | `0755` |
| `.copilot/hooks/scripts/scan-secrets.py` | `62cf4b12110d50a88bf6df4446279215b86f89bc975f357622978f06be6f01e5` | `0755` |
| `.gemini/hooks/scripts/scan-secrets.py` | `c5eecdb98bd7fac696f854613c9e31662b67a81099ddcbc4cac376c2d06f52cc` | `0755` |
| `scripts/test-scan-status-cancellation.py` | `1a3853d0a248ca6bb4d0a50124a7623737cf3c78284fc5c00ccc2f8c191b455d` | `0755` |
| `scripts/test-all.py` | `c5c534c9e9430c0a06eb34c5519b5718008fff82526dc5b95c3f617603bad79a` | `0755` |
| `scripts/test_test_all.py` | `711f44c44bda33e88324a3b8c5acaeaa7f5f84721fd320b394d2f5a36c939b71` | `0644` |
| `scripts/test-scan-secrets-lifecycle.py` | `a889bb89ce85fc4156f316d45f512ed71d36b9cedf52389f48984f917eafd852` | `0755` |

A read-only `rtk proxy python3 -` verification parsed the 22 literal runtime-input rows from [accepted T8a evidence](t8a-evidence.md), checked every current SHA-256 against that table, and compared every byte with `git show 08c472eaf702b6863baaaaf3134b8346a52e9102:PATH`. All 22 matched. It extracted the literal `MODULES` list from `hooks/runtime/scan_cli.py` with `ast.literal_eval` and reproduced the runtime's SHA-256 accumulation of filename, NUL and bytes for the exact 22-input order. The resulting neutral build remains `82e125f8e74728baf01a0e1d792d4ec131f9a309d90b861b16287482dde9b029`. The neutral runtime/installer, Guardian policy, active templates, registration mergers and gate/LFS/capacity inputs are unchanged. Their separately scoped prior evidence is reused, with no broad rerun or new acceptance claim.

## Boundaries and remaining integration

The supported repair covers ordinary POSIX SIGTERM/SIGINT delivered after the handler is installed, including input wait and a running private status group. A host that force-kills the adapter with SIGKILL cannot invoke this cleanup handler. Authentication, actual host cancellation/delivery, native Windows status containment and live installation remain separate plan obligations. Windows still returns explicit unavailable without starting an uncontained child. This task did not alter native handling, trust/enablement, scanner policy, registration, live homes or external publication.

The primary must compose this repair with T8b's migration and regenerate there rather than manually resolving generated output. The node stops after one private scoped commit and a clean worktree; no repeated background checks or checkpoint are scheduled. No new durable KB memory is proposed: the coordinated primary documentation pass owns that admission decision.
