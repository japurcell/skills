# Invalid native smokes 03

Historical observed-run checkpoint for `T4-native-pilot-03/run-01`, captured 2026-11-12. Two baseline smokes completed with native exit 0 and harness exit 2. Both are invalid qualification. Six remaining slots are gated, with zero eligible scored pairs. No retries or expansion are authorized.

## Source, setup and counts

- Source `3d5a2b5888adf77a49a000e80557bc655f19d8de`, harness SHA-256 `b5944cfdac2c5a2b7b611d8183c60e787b2256688ded5ff36f23e26c04b221a9`, manifest SHA-256 `39ae5cd8042fe280f086a7d3fa95f62aabf9af01a974b8072ce79b4446bfc889`. Requested `gpt-6.1-sol`/`medium`. Offline evidence remains 55 tests passing and independent [Standards/Spec reviews](review-startup-1.md) with zero findings each. [Source binding](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-native-pilot-03/source-binding.json), [manifest](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-native-pilot-03/run-01/manifest.json).
- Exact current approvals cover the eight-call pilot and equivalent temporary project/hook setup paths for this plan purpose under unchanged controls. Two projects and two pinned hooks were trusted. Final Codex preflight passed in 1.425 seconds. Setup and offline acceptance preceded the actual qualification failures. [Authorization](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-native-pilot-03/authorization-status.json), [Codex preflight](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-native-pilot-03/codex-preflight-receipt.json), [exact payload](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-native-pilot-03/payload-review.md).
- Two wrapper dispatches created two exclusive phase attempts and two actual evaluation sessions. The authorization field `live_model_calls=2` is interpreted at this session level. Copilot recorded seven model turns. Backend API-call count is unestablished. [Ledger](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-native-pilot-03/live-ledger.json), [raw Copilot usage](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-native-pilot-03/run-01/cells/copilot-baseline/evidence/smoke/usage.json).

| Cell | Phase | Outcome |
| --- | --- | --- |
| codex-baseline | smoke | Invalid qualification |
| codex-baseline | scenario | Gated |
| codex-candidate | smoke | Gated |
| codex-candidate | scenario | Gated |
| copilot-baseline | smoke | Invalid qualification |
| copilot-baseline | scenario | Gated |
| copilot-candidate | smoke | Gated |
| copilot-candidate | scenario | Gated |

## Copilot baseline observations

Session `7fe88737-5ebc-4a55-bd19-9cb7e36457fe` observed `gpt-6.1-sol`/`medium`. Whole wrapper elapsed was 25.195 seconds. Provider execution plus evidence collection elapsed was 17.731 seconds. The three exact helper commands were denied despite frozen grants, and the forbidden probe was denied. The neutral patch is valid. An additional unlisted `test ! -e outputs/control-forbidden.json && cat outputs/smoke-patch.json` command executed. The adapter reports 15 distinct unsupported native event types plus missing real-child and smoke checks. Selector observation alone leaves the smoke invalid. [Run receipt](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-native-pilot-03/run-01/cells/copilot-baseline/evidence/smoke/run.json), [native observations](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-native-pilot-03/run-01/cells/copilot-baseline/evidence/smoke/native-events.json), [raw stdout](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-native-pilot-03/run-01/cells/copilot-baseline/evidence/smoke/stdout.jsonl).

Raw usage reports modelMetrics requests count 7, inputTokens 50571, outputTokens 735, cacheReadTokens 42910, cacheWriteTokens 7640 and reasoningTokens 28. Its separate tokenDetails input tokenCount is 21. These fields retain their provider-defined names without reconciliation. Raw totalApiDurationMs is 13833 and totalPremiumRequestCost is 1. Adapter usage is unavailable and the missing-usage artifact remains. [Raw usage](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-native-pilot-03/run-01/cells/copilot-baseline/evidence/smoke/usage.json), [adapter availability](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-native-pilot-03/run-01/cells/copilot-baseline/evidence/smoke/usage-missing.json).

## Codex baseline observations

Session `01a1d023-4d76-7e83-8a23-8f1fbaf3cffb` completed the register, complete and smoke-write helpers plus neutral patch, and the forbidden probe was denied. Whole wrapper elapsed was 29.739 seconds. Provider execution plus evidence collection elapsed was 27.787 seconds. Native observations report `Codex-context-invalid:Codex rollout turn context mismatch`. The run receipt subsequently reports missing `codex-context.json`, masking that earlier context failure. Adapter observed model/effort are null, so executing selector qualification remains unestablished. [Native observations](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-native-pilot-03/run-01/cells/codex-baseline/evidence/smoke/native-events.json), [run receipt](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-native-pilot-03/run-01/cells/codex-baseline/evidence/smoke/run.json), [raw stdout](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-native-pilot-03/run-01/cells/codex-baseline/evidence/smoke/stdout.jsonl).

Raw `turn.completed` usage reports input_tokens 72904, cached_input_tokens 55040, cache_write_input_tokens 0, output_tokens 659 and reasoning_output_tokens 0. These zero values are observed fields. The native adapter retains the same usage projection, while the missing context prevents valid overall phase evidence. No cost is estimated. [Raw stdout](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-native-pilot-03/run-01/cells/codex-baseline/evidence/smoke/stdout.jsonl), [native adapter evidence](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-native-pilot-03/run-01/cells/codex-baseline/evidence/smoke/native-events.json).

## Remaining work

Read-only investigations of these actual contracts are next under external `T4-native-phase-codex` and `T4-native-phase-copilot` evidence. Their findings and any new correction contract remain pending. This report establishes no score or scheduler efficacy conclusion. Preserve the current frozen run and the [machine-readable report](pilot-smoke-03.json). No replacement calls are assumed approved. Native qualification, meaningful both-provider comparison, reporting and plan closure remain incomplete.
