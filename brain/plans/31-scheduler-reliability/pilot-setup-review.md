# Prepared pilot setup and native-auth investigation

Checkpoint: 2026-11-12. Source correction is verified; live pilot prerequisites remain incomplete. No live pilot call is approved or attempted.

## Pinned package

- Source commit: `2470dac6f5ed0fb17577bf5e9155e5a292e44a28`. All 38 affected tests passed on final bytes; the independent reviewer verified closure of the reported EOF defect. The original third broad review and its limited closure remain separate records.
- Harness SHA-256: `3f57143af2dfa8faf4507910e249a4d99f021486579945c4f69c43734f6439bd`.
- Manifest SHA-256: `c3412dc75e7549263265488f970927c48c96c0006a4ef17adf826d0b96ca693b`.
- [Source archive receipt](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-accepted-payload/source-receipt.json), [source acceptance record](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-accepted-payload/qualification-source-status.json), [frozen manifest](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-accepted-payload/run-01/manifest.json), [exact prompts, native argv, settings and write roots](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-accepted-payload/proposed-calls.json).
- Requested native settings remain `gpt-6.1-sol`, `medium`, 600 seconds per call. The ceiling remains eight calls, four smokes and four scenarios, serial fresh sessions with no retries. Both variant smokes must qualify before either scenario for a provider.
- The archive has no Git metadata; its original commit plus archive/file digests establish provenance separately from nullable manifest revision fields. All six frozen version-2 baseline hashes were reverified.

## Current prerequisites

- The frozen token-only harness preflight exits 2 with no supported environment token. This remains historical package evidence. The user confirms native terminal Copilot is authenticated and approved agent-owned investigation of provider-owned reuse under isolation; token absence does not establish provider-wide authentication state.
- Exact supported authentication architecture is pending `T4-native-auth/feasibility.md` by `/root/qualification_spec`. Provider-owned existing keychain auth/status reads are authorized. No credential extraction, copying, hashing/logging, login/logout or global configuration mutation is authorized.
- Preserve this frozen package and its exact [private orchestrator environment](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-accepted-payload/orchestrator-environment.json). If reuse is supported, perform the bounded TDD source correction and independent review required by the [current plan](ExecPlan.md#current-native-auth-authorization-and-task), then create a fresh payload and non-inference preflight. Exact eligible live calls still require separate approval.
- Codex: fresh project state produces the expected configuration warning. New project/hook trust and private authentication have not been changed. Existing approval applied only to the older `T4-current-payload` paths.
- Current Codex exec evidence cannot establish required executing-selector and hook-use correlation. Its scored cells remain ineligible even if authentication/trust is completed. Further Codex setup would not remove this evidence limit; no Codex call is ready for approval at this checkpoint.

## Fresh Codex cells, currently untrusted

| Cell | Exact project | Pinned hook file SHA-256 |
| --- | --- | --- |
| codex-baseline | [/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-accepted-payload/run-01/cells/codex-baseline/repo](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-accepted-payload/run-01/cells/codex-baseline/repo) | `4d46b8774f0fe69ff3716b9b86494540d86e9a0e281a5be2cdffdb7a6c137d62` |
| codex-candidate | [/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-accepted-payload/run-01/cells/codex-candidate/repo](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-accepted-payload/run-01/cells/codex-candidate/repo) | `0eae651dca5af5d9ee676b716e9608a4e6aa7ed49c1220d8f06fb3106a180c7f` |

No trust, sign-in, credential-copy or global configuration action is authorized by this report. These paths identify the prepared artifacts, not a request to repeat setup that cannot currently yield a qualified Codex comparison.

## Evidence and next action

- [Preparation and no-inference command ledger](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-accepted-payload/offline-command-ledger.json), [Codex prerequisite diagnostic](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-accepted-payload/preflight-codex.stderr.txt), [Copilot prerequisite diagnostic](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-accepted-payload/preflight-copilot.stderr.txt), [zero-attempt ledger](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T4-accepted-payload/model-call-ledger.json).
- [Third-review EOF closure](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/review-qualification-r3/closure.md) establishes only the reproduced finding is resolved; it is not a fourth broad review or native qualification.
- Next agent step is feasibility for the existing native login, then bounded correction/review if supported, fresh payload/preflight and remaining pilot/report after exact call approval. The user requested continuation until completion or justified closure; no inconclusive closeout/archive follows merely from absent environment tokens.
- [Latest readiness refresh](/private/var/folders/gx/mt30j4xd1zq0cyt0mp86q8300000gn/T/scheduler-reliability-qq1u65jw/T5-closeout/readiness-refresh.json) records two no-inference exit-2 checks and zero calls. Contract-review is advisory hypothetical analysis; no final closeout reports were written.
