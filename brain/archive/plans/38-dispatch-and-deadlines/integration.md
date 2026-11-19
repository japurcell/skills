# I1. Integrate and review the selected revision

I1 owner: integration coordinator; requires S1, E1, W1, P1 and N1 or applicable passing baselines. Run scheduler and router suites, controlled grader, skill-source validation and diff check, then independent standards/specification review. Select only passing wording. Retain separate baseline, shorter challenger, selected word counts and live evidence. Archive todo 38 only when every accepted case has evidence. If externally blocked, integrate independently verified work and preserve the open item, sources, failed attempts and exact remaining action.

## Review correction R4

The standards reviewer found that the aggregate runner omits all four new maintained orchestration suites. Register them and the exercised scheduler suite in `scripts/test-all.py`. Extend the runner's independent completeness check, reproduce the omission with the public listing, verify the new suite entries and run the affected tests. Keep native provider trials opt-in. The pre-existing scheduler suite also belongs in aggregate verification. The specification review found no substantive discrepancy. Recheck the corrected integration revision before archive.

### R4 evidence

The original public `python3 scripts/test-all.py --list` omitted the four offline orchestration suites and `test_scheduler.py`; the independent completeness test failed with exactly these five paths missing. Registered all five suites and extended completeness discovery to `scripts/tests/orchestration`. The runner completeness suite (14 tests), scheduler CLI suite (17 tests), and orchestration suites `test_controlled.py` (9), `test_heartbeat_probe.py` (3), `test_native_gate.py` (22), and `test_w1.py` (10) pass. Provider trials remain opt-in.

## Verification and disposition

The implementation and evidence changes were reviewed from `b78745922006aef8c434e67eac7b56b443fe60ee` through `99b0d46e3ef3aee714b86a80a396d1c0ad69142f`. The merge base equals the starting commit and the captured three-dot diff has SHA-256 `ea0f400f96072556ddfaa9256afd3f3c2975a61c7c43535d8608e19e4b592454`. The first independent standards review found the missing test registrations. The independent specification review had no substantive finding. The standards recheck at `9a4dea58f7a5e79a06ff826e8ec1026067831772` passed. The specification recheck found no implementation issue and identified one ambiguous use of “model” in the P2 results. The reported 6/6 now explicitly refers to the requested model. The second pinned full-range diff has SHA-256 `75eeb6322736fa158ad5abe246ade07e5d44f0d01cfbf71ab14aad490912735c`. Closure moves the completed plan and fixes its links.

The combined checkout passed 17 scheduler, 26 router and 44 offline orchestration tests. Skill-source validation and the revision-range whitespace check passed. The repository aggregate command passed all 33 suites with exit 0 in 307.9 seconds on macOS. Host-specific skips were reported by the existing suites. All five newly registered offline suites ran. No provider credentials or historical event stream were copied into the repository.

Each accepted requirement has an evidence owner. [S1](scheduler.md) verifies idle silence and legacy behavior. [E1](controlled.md) and [E2](missing-evidence.md) cover the one-extension limit, transfer with an independently observed writer, same-worker continuity, replacement handoff and the six-field status report. [N1](native-replay.md) verifies early completion and a silent-worker deadline on each host and caller. [N2](writer-shutdown.md) separately grades stop timing and continued writes. [P1/P2](paired-dispatch.md) grade the native dispatch gate and report missing actor or host metadata. The user excluded surfacing user-only invocation requirements.
