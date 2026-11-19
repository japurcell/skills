# Controlled orchestration evidence

For a live two-worker trial on Copilot CLI or Codex, use the [native lifecycle replay](native-lifecycle.md).

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
