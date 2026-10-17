# Core fixture-preflight observer repair

Status: retain the verified observer CLI fix and 28 core public tests. The optional scanner diagnostic launchers, inner traces and diagnostic-only canary test are removed. The historical source-filter `incomplete_scan` remains unexplained; no cause or fix is claimed for it. Primary owns later rebase, integration and current-tree CI.

## Current scope

`scripts/verify-security-fixture-patch.py` is unchanged by simplification: SHA-256 `bfdbe9ddc8d42ad45fd7b5b4b597acb88e4e189acdeaa2c06c51dafd7222d0d0`, mode 0755. The standalone-CLI core test script is restored byte-for-byte from owned repair `c53c56f3`: SHA-256 `7c13235b7bc6827af6ed9f866d575762c2213b7089dda95629096b5c599375e3`, mode 0755.

A static AST comparison confirms that all 28 core methods remain unchanged. Source-filter assertions are identical after removing only the optional diagnostic argument: clean verification, credential denial, no source-filter execution, unchanged target bytes and unchanged index. The 0.3/0.65-second ordinary observation, stalled observer, resistant separate-session cleanup, canonical Git-session cleanup, stdin, broken-pipe, scanner faults, redaction and other live-state controls remain. This deletes an optional diagnostic feature; no deletion regression test or replacement telemetry is added.

## Original failure and retained repair

Actual [macOS run 38983363556/job 117249097029](https://github.com/japurcell/skills/actions/runs/38983363556/job/117249097029), published snapshot `4b52fec3f43c65801cceb6c999fd489f9019d032`, ran 28 methods in 281.088 seconds. Broken-output verification exceeded 15 seconds; stdin verification exceeded 20; scanner timeout took 16.883335 seconds against its 16-second assertion; delayed metadata took 0.621 seconds against a 0.5-second allocation. These were distinct observed failures, not proof of one cause. Complete log: `/private/tmp/design-b-preflight-repeat-38983363556.log`, SHA-256 `03bc64331a4ac9300deaa9c36e136ec11eedf83e1dc56c130042b0509067edb6`.

The retained CLI repair avoids redundant full-host observations only after leader exit is established before a fresh snapshot and no remembered owned descendant remains alive. Active children retain observation, ancestry and exact identity checks. On macOS/BSD, kernel exit notification avoids the timed-wait polling overhead; exact-child reaping shares the remaining allowance after exit notification or a disappearing PID. The API was checked against the [Python 3.13 select documentation](https://docs.python.org/3.13/library/select.html#kqueue-objects) and [Apple kevent manual](https://developer.apple.com/library/archive/documentation/System/Conceptual/ManPages_iPhoneOS/man2/kevent.2.html).

Observation can use up to one second, half the existing absolute two-second cleanup envelope. Product limits remain 180 seconds per invocation, 12 per child, two for stdin and cleanup, 1 MiB of process metadata and 256 observed processes. Numeric process metadata, exact ownership, redaction, verification-only target/index behavior and independent active/candidate credential controls remain. No product behavior, limits or retry policy change in this simplification.

## Historical scanner-incomplete observation

Actual [macOS run 38985093967/job 117254593835](https://github.com/japurcell/skills/actions/runs/38985093967/job/117254593835), snapshot `c2fa8af414a9e33b02c0c4e426a4f98222a19efe`, passed the original timing/cleanup controls but failed the source-filter clean assertion with exit 2, `incomplete_scan`, phase `scan`, no findings. Full 28-method runtime was 163.495 seconds. Log: `/private/tmp/design-b-failed-38985093967.log`, SHA-256 `709dd190696fb0654c6aeb4415b5e0bb3e299ca23895b3c24352172bbc7be217`. Its cause remains open.

A later instrumented [normal macOS job 117261498554](https://github.com/japurcell/skills/actions/runs/38987254251/job/117261498554) passed 29 methods in 181.103 seconds, including the then-optional canary, followed by the scanner suites and 12 Darwin cases. That older result does not explain the historical failure or prove the current simplified tree. Log: `/private/tmp/design-b-t1-inner-full-job-117261498554.log`, SHA-256 `520ddd6aca5021655e85c35196902b7a494707baa1ac857a34744b697cba5c2a`. Complete pre-simplification evidence remains in repository history at `7dc91a5b806fb2363e57ea046ff324b3b50c02dc:docs/hook-resilience-design-b/t1-ci2-evidence.md`.

## Simplified core proof

Exactly one full simplified run is authorized, on Python 3.13.14:

    rtk proxy /Users/adam/.pyenv/versions/3.13.14/bin/python3 scripts/test-verify-security-fixture-patch.py

Frozen script identities: `/private/tmp/t1-ci2-simplified-core-freeze.json`. Complete current log: `/private/tmp/t1-ci2-simplified-core-python313.log`, SHA-256 `c72c8a729571a8791209ce3b2505cae581da8c00a9a1362fff6cefd9cb20a98c`. The one authorized invocation passes all 28 methods in 112.568 seconds. Resistant separate-session cancellation is 1.066603 seconds with 28 processes stopped; ordinary 0.3-second latency verifies in 6.216585 seconds with 110 stopped, 0.65-second latency in 6.806637 seconds with 110 stopped, and the stalled observer is bounded at 1.046312 seconds with one stopped. All unchanged target/index, source-filter clean and credential-negative, timeout and other fault assertions pass. No second interpreter or repeated run occurs. The local functional window is released; primary must provide a current base before any later rebase.
