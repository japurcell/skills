# Native macOS LFS qualification timeout

## Observed failure

HooksecurityPOSIX run `39818894888` ran `scripts/test-scan-secrets-lfs.py`
with the verified Git LFS 3.8.0 fixture on macOS. The
`test_hundreds_of_tiny_distinct_payloads_have_no_hidden_metadata_cap` case
timed out in its uncapped `git push fixture main` subtest at the unchanged
30-second `subprocess.run` bound. The full run reported 44 tests in 161.639
seconds with one error. The 900 distinct payloads, hidden-cap control, and
exact uploaded-byte assertions are required parts of this case.

## Reproduction and cause

An unchanged local run on native macOS with Python 3.13.14 and the existing
Git LFS 3.8.0 fixture passed in 27.037 seconds. A profiled repeat measured
9.450 and 9.972 seconds for the capped and uncapped pushes and observed 909
loopback HTTP connections. The endpoint inherited Python's HTTP/1.0 default,
which closes each connection. Git LFS basic transfer sends one PUT for each
object, so this fixture created a new connection for every tiny payload.

An in-memory HTTP/1.1 trial of the identical public case observed one HTTP
connection, push times of 7.720 and 8.652 seconds, and all 900 exact-byte
assertions passing. This isolates connection churn as avoidable fixture work.
The hosted timeout did not include a per-phase trace, so the fraction of its
30 seconds spent on connection setup is an inference from the local profile,
not a directly measured hosted value. The local timing difference alone is
too small to claim a fixed speedup on hosted hardware.

Python documents that `BaseHTTPRequestHandler` defaults to HTTP/1.0 and
permits persistent connections with HTTP/1.1 when responses carry accurate
`Content-Length` headers. This endpoint already sets that header for both
its POST and PUT responses. Git LFS documents a separate basic-transfer PUT
for each object. Sources: [Python 3.13 HTTP server documentation](https://docs.python.org/3.13/library/http.server.html#http.server.BaseHTTPRequestHandler.protocol_version),
[Git LFS basic transfer specification](https://github.com/git-lfs/git-lfs/blob/main/docs/api/basic-transfers.md#uploads).

## Repair and validation

`RecordingEndpoint.Handler` now sets `protocol_version = "HTTP/1.1"`. The
scanner, uploader configuration, 20-second downstream deadline, 30-second
outer subprocess deadline, 900 payload count, hidden-cap control, and every
assertion remain unchanged.

After the edit, the same public case passed in 25.688 seconds, with pushes
of 7.634 and 8.184 seconds and one HTTP connection. The complete native LFS
suite passed: 44 tests in 68.368 seconds. The local commands selected the
existing Git LFS 3.8.0 artifact through `TEST_GIT_LFS` and `PATH` and used
Python 3.13.14. `scripts/generate-hooks.py --check` reported all 60 generated
files current, and `git diff --check` passed. A fresh hosted macOS
qualification is still required to establish whether this removes the
intermittent hosted timeout.
