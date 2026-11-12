# Failed native pilot startup 02

Historical checkpoint for frozen `T4-native-pilot-02/run-01`, captured 2026-11-12. This report remains the record of this failed payload when a replacement pilot runs. The plan and live comparison remain incomplete.

## Identity and authorization

- Source `47e2a2866d474caf53eb46516dfbec5396763c61`.
- Harness SHA-256 `02d3a7b2d18b990742fc4747afb236b088dec3ad1bc460d925c61a8ef9a6f4c1`.
- Manifest SHA-256 `9e7ae0202c8cfa9e6781558be553ca651255085921d177b640644b46fff4cf3e`.
- Requested `gpt-6.1-sol`, `medium`, at most 600 seconds per call. The exact approval covers eight intended slots, four smokes and four scenarios, with no retries or expansion. Setup approval covers the two listed projects and two pinned hook definitions. Both scoped setups were applied through native UI. Setup question `call_523fe385c60141b8abd420e715bc8926`. Pilot question `call_7d1c23784af440f7823a6b92b637b306`. [Authorization](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-native-pilot-02/authorization-status.json), [exact payload](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-native-pilot-02/payload-review.md).
- Preparation and both no-inference preflights passed. Copilot preflight took 3.913 seconds and Codex 1.208 seconds. These observations establish their setup checks. Native startup and smoke qualification subsequently failed. [Preparation](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-native-pilot-02/prepare-receipt.json), [Copilot preflight](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-native-pilot-02/copilot-preflight-receipt.json), [Codex preflight](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-native-pilot-02/codex-preflight-receipt.json).

## Observed attempts

Two wrappers were dispatched. Only Copilot created an exclusive phase-attempt record. Zero model calls occurred and zero scored pairs are eligible. The remaining six intended slots stayed gated. [Startup outcome](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-native-pilot-02/startup-outcome.json), [wrapper ledger](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-native-pilot-02/live-ledger.json).

| Cell | Phase | Result | Wrapper wall seconds |
| --- | --- | --- | --- |
| codex-baseline | smoke | Codex pre-attempt discovery failure | 1.018 |
| codex-baseline | scenario | Gated | Unobserved |
| codex-candidate | smoke | Gated | Unobserved |
| codex-candidate | scenario | Gated | Unobserved |
| copilot-baseline | smoke | Copilot parser invalid | 4.998 |
| copilot-baseline | scenario | Gated | Unobserved |
| copilot-candidate | smoke | Gated | Unobserved |
| copilot-candidate | scenario | Gated | Unobserved |

Copilot baseline smoke returned harness exit 2 and native CLI exit 1. Its native process took 0.072 seconds inside the 4.998-second wrapper. The native diagnostic was `error: the argument '--session-id <id>' cannot be used with '--trust-folder'`. Stdout was empty, no session/turn/tool event was produced, and smoke qualification is invalid. [Attempt](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-native-pilot-02/run-01/cells/copilot-baseline/evidence/smoke/attempt.json), [run](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-native-pilot-02/run-01/cells/copilot-baseline/evidence/smoke/run.json), [stderr](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-native-pilot-02/run-01/cells/copilot-baseline/evidence/smoke/stderr.txt), [stdout](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-native-pilot-02/run-01/cells/copilot-baseline/evidence/smoke/stdout.jsonl), [native events](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-native-pilot-02/run-01/cells/copilot-baseline/evidence/smoke/native-events.json).

Codex baseline smoke returned harness exit 2 in 1.018 seconds with `scheduler-pilot: private discovery drift`, before exclusive phase-attempt creation or provider inference spawn. The original failed discovery delta was discarded and remains unknown. Current paired native samples match their preflights. [Wrapper stderr](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-native-pilot-02/codex-baseline-smoke.stderr), [Codex investigation](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-startup-codex-notes.md), [paired samples](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-startup-codex-paired-samples.json).

Usage, tokens and cost are unobserved. They are neither estimated nor substituted with zero. No score or scheduler efficacy conclusion follows from these startup failures. [Usage availability](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-native-pilot-02/run-01/cells/copilot-baseline/evidence/smoke/usage-missing.json), [machine-readable report](pilot-startup-02.json).

## Grounded follow-up

The installed Copilot parser rejects all four frozen argument arrays and accepts each corrected array when only `--session-id` becomes create-only `--new-session-id`, retaining the exact UUID and ephemeral folder trust. Runtime session creation remains unverified. Codex compares entire discovery dictionaries including validated asynchronous notification observations. Presence/order variance is a structural defect, while the original failure's precise cause remains unproved. [Copilot findings](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-startup-copilot/findings.md), [parser proof](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-startup-copilot/parser-evidence.json), [Codex findings](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-startup-codex-notes.md).

The [startup correction contract](ExecPlan.md#t4-startup-bounded-native-startup-correction) requires public E2E reproductions, strict maintained regressions, final-byte verification and independent new-scope review. Preserve this frozen payload without repair or retry. Review and explicitly approve a fresh frozen payload before replacement live calls. This report records blocked startup and leaves M2/T4/T5 incomplete.
