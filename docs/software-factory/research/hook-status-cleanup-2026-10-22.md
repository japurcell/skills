# Native status-adapter descendant cleanup

The macOS security job `39805598319` ran the public 32-case provider lifecycle
suite. Its Gemini rapid-root-exit fixture spawned a sleeping descendant and
returned `{}`. Immediately after the adapter returned, the unchanged `/bin/ps`
assertion saw that descendant in `?<E` state, rather than absent or zombie. The
suite failed after 59.524 seconds, with a maximum adapter time of 0.774508
seconds across 117 callbacks. The adapter had sent SIGKILL to its private
process group and waited for the root process only. A completed root did not
establish that its descendant had completed exit.

The fix keeps the existing 0.70-second child deadline, 0.10-second cleanup
allowance, and one-second public return assertion. After SIGKILL and a bounded
root wait, the adapter checks only its invocation's private group. A missing
group proves absence. If the group still exists, fixed `/bin/ps -g <group> -o
stat=` reports process states without command lines. The adapter observes until
every reported member is a zombie, the group disappears, or the existing
cleanup deadline expires. It never signals a saved descendant PID. macOS's
local `man ps` defines `-g` as selecting a process group leader and `Z` as
zombie; a native probe selected one disposable private group. On Linux,
[procps-ng ps(1)](https://man7.org/linux/man-pages/man1/ps.1.html) documents
numeric `-g` as session selection, and `start_new_session=True` gives the
status child that private session. Native Linux validation remains pending.

The unchanged public fault test passed locally once before the fix, with a
0.749234-second maximum across 21 callbacks. A disposable 24-descendant
rapid-exit scheduling probe passed 50 local repetitions, so it was not retained
as a regression test. The hosted `?<E` result is the observed red case. After
the fix and final deadline adjustment, the unchanged full native suite passed
all 32 tests in 42.555 seconds, with a 0.728624-second maximum across 117
callbacks. `scripts/generate-hooks.py --check` reported all 60 files current,
and the 25-case generator suite passed with the required worktree write access.
The generator updated three status adapters and six one-line `DIAG_BUILD`
metadata references to the status asset.

This observation covers descendants that remain in the private process group
used by the original fixture. A descendant that creates a different session
escapes the existing group signal boundary. A denied or timed-out process
snapshot, or a live member still exiting when the hard cleanup allowance ends,
cannot establish immediate absent-or-zombie closure. The adapter still returns
its bounded informational status in those cases. Local green does not establish
that the intermittent hosted scheduling failure is resolved; a fresh hosted
macOS run is needed for that qualification.
