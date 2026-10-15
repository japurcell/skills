# T9: deterministic observability fixtures

Completed on 2026-10-14 from `8af2e8cf9b798aa435eff46974228d1c8208e2c5` on private branch `codex/hook-resilience-t9`. Scope is the installed-copy fixtures in `scripts/observability-test-support.sh`. The coordinator owns plan changes, final knowledge maintenance and release acceptance.

## Diagnosis and preserved red evidence

V1 evidence at commit `ca51a464b2dedc6de83fd6d46508afc544f0fe77`, `docs/hook-resilience/V1-phase1-evidence.md`, preserves two uninstrumented Gemini failures: exit 5 with `Error: stepping, database is locked (5)`, then exit 1 removing a nonempty disposable `.gemini/hooks` directory. Its surviving empty database and fresh sentinel implicated detached maintenance in an unrelated fixture. V1's original failing SQL statement remains unidentified. Its invalid DEBUG/functrace attempt is excluded.

T9 first ran the unchanged public Gemini suite; it passed with all three completion markers. Ten unchanged persistence-fixture repeats also passed. These establish intermittency and do not erase V1's failures.

The installed runtime still triggers detached maintenance after lifecycle events under `OBSERVABILITY_FORCE_NDJSON=1`. Six ordinary rotation fixtures lacked the fresh `.maintenance_last_run` required by `.agents/instructions/testing/hooks-observability.md`; the later fail-open fixture already had one. An external launch observer forwarded every actual subprocess and failed the unchanged installed-copy fixture:

```text
FAIL: test_observability_log_rotation launched detached maintenance before fixture cleanup
args: [python3, -m, helpers.observability, --maintenance]
exit=1
```

A separate controlled installed-copy reproduction identified a concrete SQLite race in `test_sqlite_observability_persistence`. Its first SessionEnd can start maintenance before it deletes and rewrites the database for schema recovery. External `sitecustomize.py` held the real maintenance child's actual `BEGIN IMMEDIATE` behind an event-file barrier. The existing SQLite CLI then ran with its unchanged default timeout, and its wrapper released the child after recording the result. The child also had a five-second safety deadline. The unchanged fixture failed:

```text
PERSISTENCE_ATTEMPT=1
SQL: PRAGMA user_version = 42;
Error: stepping, database is locked (5)
exit=5
```

This proves a concrete fixture lock race with V1's error signature. It does not identify V1's untraced statement. The launch proof establishes an unwanted background writer but does not claim a new uninstrumented reproduction of V1's exact `rm` diagnostic.

## Repair

`seed_recent_observability_maintenance()` creates the fixture log directory and fresh sentinel. Six rotation scenarios and the persistence schema-mutation scenario call it immediately after installing into their disposable HOME. This applies the existing isolation rule before destructive setup and cleanup.

Intentional maintenance fixtures and their explicit maintenance entrypoints, retention/scavenging checks, lock-wait fail-open coverage, cleanup traps and assertions remain intact. No global maintenance disable, retry, suppressed cleanup error, runtime edit or weakened assertion was added. Both provider suite files are unchanged.

## Verification

Commands ran from the assigned worktree with disposable HOME/CODEX_HOME state and fake credentials. No global AUDIT_LOG or provider/generic observability path overrides were injected. Each fixture installed real copied hooks. No aggregate, benchmark, authenticated provider delivery, live-home install or generated-source write ran.

The same controlled SQLite reproducer passed after repair (`PERSISTENCE_OK=1`, exit 0). All six initial Gemini rotation observer cases passed with zero maintenance launches. `rtk proxy bash -n scripts/observability-test-support.sh scripts/test-hooks-observability.sh scripts/test-gemini-hooks-observability.sh` passed.

The following checks ran serially. Durations are functional evidence, not release-performance measurements.

| Check | Exit | Seconds |
| --- | ---: | ---: |
| `copilot-suite` | 0 | 31.984 |
| `gemini-suite` | 0 | 34.027 |
| `copilot-rotation-repeat-1` | 0 | 8.631 |
| `gemini-rotation-repeat-1` | 0 | 9.293 |
| `copilot-rotation-repeat-2` | 0 | 10.658 |
| `gemini-rotation-repeat-2` | 0 | 9.030 |
| `copilot-rotation-repeat-3` | 0 | 9.375 |
| `gemini-rotation-repeat-3` | 0 | 9.216 |
| `gemini-persistence-10-green` | 0 | 28.954 |

`copilot-suite` is `rtk proxy bash scripts/test-hooks-observability.sh`; `gemini-suite` is `rtk proxy bash scripts/test-gemini-hooks-observability.sh`. Both printed `CYCLIC_TEST_OK`, `MOCK_FCNTL_OK` and `ADDITIONAL_OBSERVABILITY_SCENARIOS_OK`. Every rotation repeat executes all six repaired scenarios, retains rotation/pruning/precedence assertions, and requires zero maintenance launches. This gives 36 repeated installed-copy rotation scenarios across both providers, plus the initial six Gemini green checks. The final persistence check runs the repaired fixture ten times with SQLite CLI statement logging.

## Instrumentation and retained artifacts

External harnesses and raw logs remain in `/private/tmp/hook-resilience-t9/` for coordinator retention. Provider probes copy each public suite only through its function definitions, before `main()`, replace its initial test-common source with the absolute original path, and load maintained shared support unchanged. They do not enable DEBUG/functrace or alter RETURN cleanup traps. The rotation probes set `OBS_TEST_PYTHON` to `observe-python.py` and FORCE_NDJSON, call the six ordinary rotation functions, and fail if a maintenance launch was recorded. The observer wraps `subprocess.Popen` to record maintenance arguments/HOME and forwards the actual call. Installed scripts run through `runpy.run_path` with their original directory on `sys.path`.

The controlled persistence probe uses original fixture definitions, external SQLite CLI logging and temporary PYTHONPATH for `controlled/sitecustomize.py`. Only the process with `--maintenance` gets a SQLite connection subclass. After an actual `BEGIN IMMEDIATE`, it creates `t9-maintenance-holds-lock` and awaits `t9-release-maintenance` or the bounded deadline. The CLI wrapper awaits that holder only for `PRAGMA user_version = 42;` when a child launch was observed, runs the real CLI and releases maintenance. The repaired fixture has no launch marker, so the same harness executes normal CLI statements. This is synchronization at the observed seam, not an arbitrary delay or shipped runtime change.

Raw logs/statuses, both provider probes, observer/barrier sources, failing SQL JSON, repeated fixture logs and `verification-summary.json` are retained. SHA-256 hashes pin decisive artifacts:

| Artifact | SHA-256 |
| --- | --- |
| `gemini-original.log` | `6ee23826b08730a0ec2e51eefb2ba4ffde3df958bbf8b20180665021aac0c91a` |
| `gemini-rotation-red.log` | `c04d46e5bb9e06aa4de71bf02656860c5549cdc0adaabd748af1c570b0dc9f7b` |
| `gemini-persistence-red.log` | `8ee3b62cbbff7356570ce903b43377c835425cfdd03a436e84c6d8e348e6f2f8` |
| `gemini-persistence-controlled-red.log` | `3964c00d779b86b16d31141f1da66bf2ca0049b54543e8c362fee4d118df2caa` |
| `controlled-lock-failures.json` | `199160f02c3544e328a6fd0e4fb50db87e1998fb87a99053604fa1d29abc39a9` |
| `gemini-rotation-green.log` | `fd6539c01b6dd6f5c0e60707108e7eb3ef0c7299f63be545f835e8b139fab015` |
| `gemini-persistence-controlled-green.log` | `d94d7a7a299b4bd143af850a6747f9d80bc40e2882e09e33e9621dde2924b746` |
| `copilot-suite.log` | `6ee23826b08730a0ec2e51eefb2ba4ffde3df958bbf8b20180665021aac0c91a` |
| `gemini-suite.log` | `6ee23826b08730a0ec2e51eefb2ba4ffde3df958bbf8b20180665021aac0c91a` |
| `verification-summary.json` | `85b35cb509b703243296e317da4c90675b06fb4f076e6d01862deaf6842fd9d7` |
| `observe-python.py` | `2ac71aa302c26bf85ca8262c2b19b678847f34049f9d4938a941b87356862dfb` |
| `controlled/sitecustomize.py` | `677e9c2f5ae01210c801c16951f609c96a1b00e39902e3e2578e346e8a8d51ac` |
| `bin/sqlite3` | `3ea083cf7abb90ca90df949bfbbf967811137a02fbb573e14adb633d05e209b1` |

## Limits and ownership

The established causes are fixture interference; no runtime defect was established or patched. V1's untraced original statement remains uncertain. Targeted repair does not establish release acceptance, native Windows behavior or provider delivery. The coordinator must integrate this commit, complete the single final knowledge-maintenance pass and have V1 repeat affected release checks with its corrected environment. No skill improvements identified.
