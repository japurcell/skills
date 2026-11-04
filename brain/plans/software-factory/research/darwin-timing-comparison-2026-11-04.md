# Darwin selector timing comparison

Read-only comparison of the three retained complete schema-2 exports. All three have 2,161 records, 31 original fixtures, fixture exit 0, and 51 workers (48 self-closed, 10 parent-observed bound closures). No artifact was modified.

## Normalized run metadata

| Run | Source SHA | Runtime SHA-256 | Node | Host/runtime | Available parallelism | Runner image |
| --- | --- | --- | --- | --- | ---: | --- |
| A / closure baseline | `b3d7cc77ca1a8e16e164d24ff307805252f81faa` | `6f32069480ec14d52b6d7b1f3c7124cfbbc46203abf5ddf5c65b127435f3f329` | v24.22.1 | Darwin arm64, OS 24.6.0 | 3 | macos15 `20261028.0489.1` |
| B / Gemini context | `3ff05c14568220ff6ba13119df9db5862c4404a2` | same | v24.22.1 | Darwin arm64, OS 24.6.0 | 3 | macos15 `20261028.0489.1` |
| C / current context | `9fdc2307b2a61182d65afbf4667f84e901cbdd83` | same | v24.22.1 | Darwin arm64, OS 24.6.0 | 3 | macos15 `20261028.0489.1` |

All report `clock=host-monotonic-ms`, `attemptClock=persisted-utc-wall`, and `cpu=emitting-process-only`. The within-run `selector` begin/end markers are on the same worker and give 87.041s / 50.957s / 71.497s (A/B/C). The reported full fixture times are 86.918s / 50.874s / 71.390s. The monotonic offsets differ substantially; the exports do not establish a common monotonic origin, so only within-run deltas are compared. CPU attribution is limited to the process that emitted each record; no child/compiler CPU was measured.

## Selected parent results

| Run | Notifications / 15s | Learning / 30s | Full 31-fixture suite |
| --- | ---: | ---: | ---: |
| A | 14.194s | 29.508s | 86.918s |
| B | 8.466s | 16.330s | 50.874s |
| C | 9.256s | 27.709s | 71.390s |

These all passed their unchanged selectors. A has only 0.806s notification and 0.492s learning margin; B and C have more margin. The known original red run at 8f59d77b timed out at 15s/30s and has no complete old timing artifact, so it cannot be used for a same-source cause or repair claim.

## Per-case durations and within-run file timelines

The following first table sums per-case durations for each fixture file and gives its longest individual case. These are worker-duration sums, not critical path or selector wall time.

| Learning fixture | Cases | A sum; max case | B sum; max case | C sum; max case | B to C sum change |
| --- | ---: | --- | --- | --- | ---: |
| `learning-extraction-evidence.test.mjs` | 6 | 15.248s; case 1 4.866s | 8.593s; case 1 2.647s | 13.786s; case 1 4.717s | +5.193s |
| `learning-extraction-paths.test.mjs` | 2 | 10.172s; case 1 7.195s | 5.889s; case 1 4.148s | 9.456s; case 1 6.830s | +3.567s |
| `learning-extraction-sources.test.mjs` | 3 | 18.901s; case 2 11.980s | 10.240s; case 2 6.460s | 17.959s; case 2 11.241s | +7.719s |
| `learning.test.mjs` | 2 | 9.458s; case 2 6.332s | 5.118s; case 2 3.342s | 8.502s; case 2 5.270s | +3.384s |

Within each run, host-monotonic case timestamps share a run origin across worker processes. Each file cell below is `earliest case begin - latest case end (file elapsed, including gaps); ending case`, with offsets relative to the earliest selected case begin for that group in that run. These are actual within-run file timelines, not cross-run timestamp subtraction.

**Notifications, 36 selected cases.** Group case windows from first selected case begin to last selected case end are A 13.845s, B 8.286s, C 9.022s. The last-ending file/case is `notification-records-success.test.mjs` case 2 in all three runs.

| Fixture file [case count] | A | B | C |
| --- | --- | --- | --- |
| `notification-records-cli.test.mjs` [2] | 0.014-5.702 (5.688); c2 | 0.024-3.141 (3.116); c2 | 0.006-3.411 (3.405); c2 |
| `notification-reminder-uncertain.test.mjs` [1] | 0.071-5.477 (5.406); c1 | 0.027-5.177 (5.150); c1 | 0.014-5.291 (5.277); c1 |
| `notification-success-uncertain.test.mjs` [1] | 0.019-7.586 (7.567); c1 | 0.009-6.382 (6.372); c1 | 0.005-6.322 (6.317); c1 |
| `notification-sender-uncertain.test.mjs` [1] | 0.000-7.697 (7.697); c1 | 0.000-6.222 (6.222); c1 | 0.000-6.269 (6.269); c1 |
| `notification-senders.test.mjs` [9] | 7.940-8.567 (0.627); c9 | 6.282-6.760 (0.478); c9 | 6.371-6.808 (0.438); c9 |
| `notification-preflight.test.mjs` [1] | 8.786-8.878 (0.092); c1 | 6.492-6.568 (0.077); c1 | 6.405-6.485 (0.080); c1 |
| `notification-pipe.test.mjs` [3] | 9.100-10.497 (1.397); c3 | 6.621-7.783 (1.163); c3 | 6.554-7.681 (1.128); c3 |
| `notification-reminders.test.mjs` [13] | 7.968-12.425 (4.458); c13 | 5.635-7.679 (2.044); c13 | 6.379-8.535 (2.155); c13 |
| `notification-records.test.mjs` [3] | 5.564-13.425 (7.861); c3 | 3.195-5.560 (2.365); c3 | 3.467-6.207 (2.739); c3 |
| `notification-records-success.test.mjs` [2] | 5.789-13.845 (8.056); c2 | 5.283-8.286 (3.003); c2 | 5.349-9.022 (3.672); c2 |

**Learning, 13 selected cases.** Group case windows are A 29.168s, B 16.188s, C 27.517s. The last-ending file/case is `learning-extraction-sources.test.mjs` case 3 in all runs.

| Fixture file [case count] | A | B | C |
| --- | --- | --- | --- |
| `learning-extraction-paths.test.mjs` [2] | 0.008-10.181 (10.173); c2 | 0.000-5.889 (5.889); c2 | 0.004-9.461 (9.457); c2 |
| `learning-extraction-evidence.test.mjs` [6] | 0.000-15.250 (15.250); c6 | 0.000-8.594 (8.594); c6 | 0.000-13.788 (13.788); c6 |
| `learning.test.mjs` [2] | 15.357-24.821 (9.464); c2 | 8.658-13.776 (5.118); c2 | 13.871-22.374 (8.504); c2 |
| `learning-extraction-sources.test.mjs` [3] | 10.266-29.168 (18.902); c3 | 5.947-16.188 (10.241); c3 | 9.557-27.517 (17.960); c3 |

The slowest learning case in all runs is sources case 2, which contains malformed/unknown/unended/foreign reference controls. Its B-to-C increase is 4.781s, while it remains 0.739s below A. Notification slow cases are uncertainty fixtures: A's slowest is `notification-sender-uncertain` case 1 at 7.697s; B's is `notification-success-uncertain` case 1 at 6.372s; C's is the same at 6.317s. Required five-second behavior in these uncertainty controls remains in place.

## Span and attempt distributions

Tuple format is `count / summed worker-seconds / median / p90 / max`. Here p90 is the sorted sample at index floor(0.9 * (n - 1)), without interpolation. Span values come from end-record `wallMs`; attempt elapsed values are the difference between persisted `attempt.started` and `attempt.settled` event timestamps. Nested/concurrent sums are worker time and must not be added together as selector time.

| Selected group / measure | A | B | C |
| --- | --- | --- | --- |
| Learning copy spans | 13 / 4.518 / .344 / .395 / .478s | 13 / 2.275 / .167 / .184 / .261s | 13 / 3.024 / .225 / .277 / .502s |
| Learning source spans | 12 / 15.010 / 1.142 / 1.399 / 1.765s | 12 / 8.180 / .665 / .756 / .798s | 12 / 13.647 / 1.077 / 1.217 / 1.736s |
| Learning learn spans | 23 / 28.217 / 1.237 / 1.332 / 1.621s | 23 / 16.146 / .698 / .785 / .936s | 23 / 27.952 / 1.154 / 1.430 / 1.821s |
| Learning startup/build attempts | 36 / 25.885 / .676 / .834 / 1.098s | 36 / 15.325 / .406 / .489 / .611s | 36 / 24.576 / .652 / .856 / 1.097s |
| Learning fake-agent attempts | 16 / .829 / .048 / .062 / .087s | 16 / .591 / .036 / .043 / .048s | 16 / .864 / .052 / .068 / .072s |
| Notification copy spans | 9 / 2.885 / .311 / .382 / .546s | 9 / 1.245 / .129 / .180 / .193s | 9 / 1.343 / .131 / .194 / .231s |
| Notification startup/build attempts | 14 / 14.002 / .924 / 1.347 / 1.738s | 14 / 5.226 / .338 / .488 / .592s | 14 / 5.667 / .383 / .549 / .576s |

Persisted event `at` is attached by the store when each attempt event is written and is exported unchanged. Attempt `wallMs` is zero/default and was not used. These are wall-clock intervals with millisecond timestamp precision; they are not CPU time. The lower-level sums and spans help locate where observed time co-varies, but do not establish a bottleneck or cause.

## Learning-copy change and bounded interpretation

The copy-helper change narrows the learning fixture's copied `node_modules` from 839 files / 51,608,005 bytes to 651 files / 32,725,856 bytes. Five paired local copy measurements changed the median copy time from 94.632ms to 70.969ms. Separately, the 13 original learning cases stayed unchanged. The copy measurement is evidence about that operation only. The artifact copy spans in B-to-C instead rise from median 167ms to 225ms and from 2.275s to 3.024s total; the artifact runs have different source SHAs, so this is not a controlled contradiction or a controlled speed comparison.

B-to-C selected learning wall rises 11.379s. Over the same two artifacts, learning `learn` span sum rises 11.806s, `source` span sum 5.467s, copy sum 0.749s, and startup/build attempt sum 9.251s. These intervals can be nested and concurrent, and the source changes also include internal candidate/OpenCode registry work; the data does not show which one explains wall variation. No bottleneck, contention, CPU cause, or regression is established.

## Small next observation

The current data show B-to-C learning startup/build attempt wall sum rising 9.251s while copy-span sum rises 0.749s. These are nested/concurrent worker observations and do not identify a cause. A sequential copy-helper A/B would not by itself separate host load, cache state, or ordering effects, so it is not the next useful measurement.

The narrowest existing boundary is the `startup/build/<invocation>` attempt in `src/build.ts`, paired by file/case with the enclosing fixture `source`/`learn` span. The attempt interval is persisted store time from `attempt.started` to `attempt.settled`; `buildWorkflow` launches `tsc` through `CommandRunner`, whose stdout/stderr are captured, but these captures contain no compiler CPU or build subphase timings. The enclosing selector-worker telemetry records only the test worker process CPU for its broad span, not the spawned fixture host or compiler child. The current exports therefore offer broad test-worker CPU alongside compiler-attempt wall, but do not report fixture-host CPU, compiler CPU, or build subphase times. This cannot split parent build CPU from child compiler CPU or distinguish build setup, process wait, and capture/settlement time.

A bounded design is needed before proposing a more specific observation: define a qualification-only boundary around the build call and identify an already supported, cross-platform way to attribute CPU to the compiler child. Do not infer a new Node channel, add instrumentation, or launch another run from this packet. Keep selector bounds/order/assertions and five-second uncertainty behavior fixed.

## Evidence boundaries

The three source revisions differ; the exports show compatibility and timing variation only. Do not claim a repair or cause for the old 8f59d77b timeouts. Do not infer whole-suite contention, production bottlenecks, descendant/compiler CPU, or wall-time causes from sums of nested spans and attempts. No tests, builds, lifecycle runs, native operations, or new experiments were performed for this comparison.
