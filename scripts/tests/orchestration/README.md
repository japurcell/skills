# Controlled orchestration evidence

All tests below run offline. The standalone `run_actors.py` and `run_native_gate.py` commands also prepare local fixtures by default. To spend tokens on a live eval, pass the full `--allow-model-calls` option on that invocation.

For a manual live two-worker trial on Copilot CLI or Codex, use the [native lifecycle replay](native-lifecycle.md).

Run from the repository root:

```sh
rtk proxy python3 -m unittest discover -s scripts/tests/orchestration
```

`test_controlled.py` invokes the public scheduler CLI against temporary state
files. Its first case models the five-minute point while the actual deadline
is ten minutes away: state stays identical and there is no dispatch, setup read,
or parent status lookup. A negative observation with a lookup is rejected. A
second case accepts the actual, correctly addressed deadline event using the
same grader and rejects a mismatched assignment. The two-worker case completes
the nearer worker and verifies the later deadline is the next emitted event.

Expiry and extension are driven through CLI commands. A worker status response
with ETA enables one extension; a second extension is rejected. The process
transfer exercise starts separate worker and writer children, verifies the
writer is actively appending data, and verifies the grader rejects transfer
while either process is alive. After both exit it exercises
the CLI shutdown confirmation and transfer commands. The CLI confirmation is
a host assertion; it does not itself inspect processes. The test supplies the
independent process observations before allowing that command.

The continuity case uses one child process that retains a known setup fact
between messages, then starts a replacement process with only environment,
pinned revision, and evidence. The report grader requires exactly these six
fields in both reports: `owner`, `pinned_revision`, `completed_evidence`,
`blocker`, `deadline`, and `next_action`. The second report may add completed
evidence but cannot drop earlier evidence. Handoff values and worker identities
are checked against separate expected values. Negative assertions remove an
expected event or handoff evidence, claim a live worker/writer transfer, omit
a required report field, empty the blocker, or repeat setup.

These deterministic controls verify scheduler CLI behavior and fixture-grade
checks. They do not prove host dispatch, notification delivery, native agent
context retention, native worker cancellation, or that a real host has
quiesced all writes. Those require a live host run with observable process and
write evidence. The historical trace is not copied into this fixture.

`render_variants.py <outdir>` also renders the frozen W1 variants and three P2
profile-preservation arms (`p2-screen`, `p2-deletion`, `p2-final`) from exact
gate bodies in `fixtures/p2-gates.json`. Its `counts.json` reports whitespace
word counts and full caller/router SHA-256 hashes. `test_w1.py` pins all six P2
rendered hashes and counts, while retaining checks for the original P1 arms.
The checked-in replay suite uses synthetic local fixtures and does not read
private provider traces or `/private/tmp` artifacts.

For controlled dispatch case 03, the host samples its monotonic clock at command entry
and again after the primary rejection has been written to the log. Each dispatch receipt links to its start.
The grader requires exactly one primary rejection followed by one successful
routed fallback that began after that rejection was recorded. Two concurrent calls can
finish in the expected order and still fail. The per-case report retains the raw
observations in file order and flags missing or conflicting ordering evidence.
Older traces remain reportable. Case 03 requires the start evidence to pass.
