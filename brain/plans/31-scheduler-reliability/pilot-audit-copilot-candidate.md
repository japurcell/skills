# P05 Copilot candidate independent audit

Native exit0 and185.386881 seconds differ from automated qualification. Session `a9edf11a-60c0-4f5b-8821-1567aa71f86e` observed Sol/medium. Original run remains invalid with missing-real-child-receipt and receipt-from-unmatched-command, and original grade stays ineligible. This is an independently corrected offline semantic assessment, with no rerun or replacement grade.

## Actual root execution

There are17 stateful scheduler receipts, including final list, plus one parent-update receipt. Direct absolute frozen helper calls use exact pinned scheduler argv/canonical state. All before/after states form one continuous chain starting empty, with no reset/replay. Final canonical state equals the last child readback. Native calls prove direct-helper grant acceptance for exercised operations. Sanitized commands, receipts, metadata and hashes are retained in `copilot-candidate-sanitized.json`.

## Batch observations and output-contract interpretation

`outputs/result.json` has the required schema/confined paths and all required actions. Three additional request-checkpoints entries for A/B/C at100 share `outputs/04-request-checkpoints-100.json` and native tick receipt1143. That real child stdout contains three distinct A/B/C deadline_expired host requests. All required8 actions separately match unique exact command/child-exit receipts.

The current implementation rejects any reused receipt across authored rows. The active contract scopes one-to-one matching to required actions, and the rubric says actions must include the required rows. It allows truthful additional observations. Under that wording, these batch members are distinct supported events, with no repeated required action or replay. I initially treated implementation strictness as a contract violation. Rechecking the frozen rubric and actual batch output supports the contract interpretation. Recommend preserving required-action uniqueness and binding additional batch observations to distinct actual event members. No authored output was repaired, and original grade remains unchanged.

## Independent assertion observations

All line numbers refer to original `evidence/scenario/stdout.jsonl`.

| Assertion | Assessment and evidence |
| --- | --- |
| exact_output | Supported under required-action contract, with truthful distinct batch observations1143. Current implementation is stricter, as explained. |
| immutable_execution | Supported, direct helper/scoring receipts612-3299 and final list13266. |
| stop_timing | Supported, A105/B200 transitions at1989/2497 in finite nondecreasing synthetic chronology. |
| single_extension | Supported, extension200 at1656, checkpoint150 preserves it at2159, active/extended unchanged-state ETA250 rejection151 at2330. |
| exclusive_pending_shutdown | Supported, transfer201 exit2 preserves state/old owner at2662 before confirmation202 at2840. |
| independent_progress | Supported, C checkpoint102/completion104 at1484/1822 before B confirmation, B unconfirmed before/after. |
| parent_transfer | Supported, stop confirmation2840, authorization3007, actual parent write/readback3111, final owner agent-new. |

Candidate acknowledgment is separately supported at3299, exit0, after parent204. Transfer completion and receipt owner agent-new, evidence `outputs/ownership.json`, recorded_at205 match the same current target and final list13266.

## Parser flags and ancillary mistakes

Harmless source cat72 and receipt-file inspection13258 expose literal pilot_child and are misclassified as unmatched execution. Exploratory helper `--state ... --help` at46 rejects syntax, shell exit2 without receipt. Supported register-help118 returns exit0 with null before/after and is read-only.

Required rejection calls2330/2662 each have native `success=true`, `data.shellExecution.exitCode=2`, matching footer exit2 and helper receipt exit2. Transport success is distinct from command exit. Their valid receipts are discarded by the original parser.

Actual denied extras remain recorded at428 (redirected register),6122 (Python evidence-saving),13231 (Python validation). No corresponding scored state mutation occurred before accepted direct registration612. The agent retained evidence via apply_patch. These tooling mistakes and the batch-output interpretation remain separate from transport/parser errors.

Independently, seven common assertions plus candidate acknowledgment are supported under the approved required-action wording. Original automated invalidity is unchanged. No fixed efficacy claim follows from one diagnostic pair. No tests, model/provider calls or original source/evidence edits occurred.

## Retained audit provenance

[External original](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-focused-pilot-05/review/copilot-candidate.md), SHA-256 `3b311e40cb9e1113e9341823dbe1fcf25bc49c916fa9c6adccd9015c76c2fac8`. Native line references refer to that cell's original external stdout/rollout. This retained Markdown contains no raw session dump.
