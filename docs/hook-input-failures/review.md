# Hook bug fixes: independent review

Reviewed baseline `72789d6978bb7255583f9fb1cd8e18c37fe3173b` through checkpoint `5ce57e8784ad2b1243ef625e7f9dbf30bed4b958`. The two reviewers received the same complete diff and commit list. Standards received repository requirements and the full Fowler smell baseline. Spec received both bug reports, the user's Codex sampling request, the clarification that both reports came from Copilot, and the ExecPlan. Source was unchanged after this checkpoint.

## Standards

Documented-standard violation:

- **Reconcile the active plan with completed implementation and validation.** The reviewed ExecPlan's Outcomes said "Integration, composed proof, resource measurements ... remain unfinished," contradicting checked Progress entries and retained results. Context still said the scanner "currently discards the reason," despite the implemented typed diagnostics. Surprises presented pre-edit installed/source parity as current while installed refresh remained pending. These violate `AGENTS.md` Knowledge maintenance ("Cross-check factual claims against current source ... Correct stale guidance") and `.agents/skills/exec-plans/SKILL.md`, Reconcile the plan ("Replace outdated statements wherever they appear in active sections"). Update current outcomes/context and label original installed fingerprints as historical; retain the actual pending installation, review, and platform gates.

No additional actionable code/security standard violations or baseline smell findings. Generated provider duplication follows documented renderer ownership and separation requirements.

Verification limits: read-only source, diff, conventions, and retained evidence review; no fresh test reruns. At the reviewed checkpoint, installed refresh, authenticated Copilot pre-tool delivery, native Windows behavior, and the external Linux incident's exact cause remained unverified.

Resolution: coordinator repair R1 reconciled the active plan throughout. Subsequent installed refresh and direct probes passed and are recorded separately in [validation](validation.md). The same Standards reviewer independently verified R1 and reported no remaining actionable issue. Source remained unchanged, so no additional source test rerun was needed. Authenticated delivery, Windows, and the external incident's exact cause remain unverified.

## Spec

No actionable Spec findings. The reviewer found no missing source behavior, unasked scope expansion, or incorrect implementation against the two reports and active contract.

The changes classify the observed Copilot raw patch envelope, preserve strict handling for unsupported shapes and malformed patches, raise only validated patch capacity to 256 KiB, and distinguish capped segment measurements from exact totals. Protected delete/move checks remain active. Scanner failures retain denial in block mode and expose fixed, sanitized causes, operations, measurements, and recovery advice.

Independent targeted verification passed three public Guardian tests covering unsupported envelopes, malformed/trailing input, and late protected operations in large multi-file patches. Six scanner probes covering missing Git and invalid input passed across all three providers. Codex's early legacy block response is supported by [official hook documentation](https://learn.chatgpt.com/docs/hooks).

Unverified scope remains explicit: authenticated Copilot pre-tool delivery, native Windows behavior, and the original external Linux scanner cause. Public subprocess and source evidence do not establish those outcomes. Final installation and documentation reconciliation were coordinator work at the reviewed checkpoint.

Standards: 1 finding, stale active-plan statements; repaired and independently verified. Spec: 0 findings, no worst issue.
