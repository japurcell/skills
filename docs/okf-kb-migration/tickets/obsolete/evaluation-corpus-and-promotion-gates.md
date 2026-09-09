# Evaluation Corpus and Promotion Gates

**Type:** grilling
**Status:** obsolete
**Blocked By:** none
**Research Dir:** N/A

## Question

What representative task corpus, relevance oracle, baseline, metrics, thresholds, mutation cases, provider-parity checks, and latency/token measurements will prove mandatory-context preservation, non-regressing recall, stale/deprecated exclusion, and worthwhile irrelevant-token reduction before promotion?

---

<!-- Resolution will be appended here -->

## Resolution

### Accepted round 1

- Use a committed, versioned, provider-neutral, hand-reviewed corpus of realistic repository tasks. Each case records task text, normalized paths, task kind, task scope, evaluation time, budgets, and expected disposition. Coverage must include every task kind, both scopes, every mapped area, `no_match`, ambiguity, budget pressure, and all 42 concepts at least once through relevance, mandatory policy, or relationships; do not impose an arbitrary case count or generate the corpus mechanically from metadata.
- Give every case a semantic oracle of `required`, `allowed`, and `forbidden` concepts plus expected mandatory roots, disposition, lifecycle substitutions, and fallback or hard-stop reason. Use separate exact contract assertions for deterministic order, reason codes, and rendered bytes. Recall is measured against `required`; selected `allowed` concepts count as relevant but are reported separately.
- Compare against a deterministic same-revision legacy baseline that resolves the current `INDEX.md` loading procedure and area-scoped guidance. Compare only migration-controlled `.agents/` context, treat runtime `AGENTS.md` as common context outside both measurements, and store baseline document identities and byte totals while canonical documents remain the content source.
- Use absolute safety and compatibility gates before efficiency gates. Missing mandatory context, forbidden lifecycle content, wrong dispositions, nondeterminism, integrity failures, or provider divergence are zero-tolerance failures; recall, irrelevant-token reduction, and latency use declared corpus-wide and worst-case thresholds rather than averages alone.

### Accepted round 2

- Split the committed corpus into `development` and `promotion`. Freeze promotion cases and oracles within an evaluation-contract version; changing them requires a reviewed version bump and preserved historical results. Both partitions independently cover every safety disposition, while broader concept, task-kind, scope, and area coverage may span both.
- Every `use_okf` promotion case must select 100% of its `required` concepts and may not perform worse than its same-revision legacy baseline. Budget-stress cases that cannot safely satisfy the oracle must return their expected `use_legacy` disposition. Report `allowed` selection separately; it never compensates for a missing required concept.
- Use UTF-8 bytes as the deterministic hard-gate unit. No promotion case may increase irrelevant bytes over legacy. Across cases with nonzero legacy irrelevant context, require at least 30% aggregate and 20% median reduction. Report provider-native prompt-token counts when available, but do not gate on tokenizer-specific values until provider integration defines a stable measurement contract.
- Require byte-identical structured results and rendered context under a fixed perturbation matrix covering input-path order, hash seed, locale, timezone, and repeated clean-process runs. On a declared reference CI environment, cold one-shot selector latency must have p95 at or below 100 ms and maximum at or below 250 ms over the promotion corpus. Producer/checker latency is reported separately and is not a prompt-path gate.

### Accepted round 3

- Derive deterministic single-fault mutations from valid fixtures. Cover malformed or unsafe inputs; pending ingest; missing, stale, corrupt, or version-incompatible projection evidence; hash and path mismatches; invalid relationships and cycles; stale or deprecated mandatory branches; lifecycle substitution; byte and count exhaustion; `no_match`; access violations; and canonical-source drift during generation. Every mutation must produce its exact expected disposition and reason code with no partial context; every mutation case is a hard gate.
- Publish reusable adapter replay vectors from the provider-neutral corpus. Given the same normalized selector input and projection, Copilot and Gemini adapters must agree exactly on disposition, selected logical paths and order, rendered context bytes, lifecycle substitutions, and reason codes. Provider envelopes, injection mechanics, and final-response behavior may differ only where **Provider Integration and State** explicitly permits it. Both adapters must pass before promotion.
- Produce a machine-readable CI report containing its schema version; candidate commit; evaluation-contract, profile, selector, producer, corpus, projection, and legacy-baseline digests; runtime and platform identity; every case result; mutation and parity results; byte metrics; timing distribution; and optional provider-native token counts. Promotion accepts only a complete report from the exact candidate commit. Commit corpus cases, oracles, replay vectors, and expected contract outputs; retain full run reports as CI artifacts rather than repository source.
- Require human review for every corpus or oracle change and record its reason. Keep selector changes separate from promotion-oracle changes for review, and never weaken an oracle merely to admit a candidate. New concepts, policy rules, reason codes, or discovered failures must update coverage before promotion. Preserve historical evaluation versions and results reproducibly; change a gate only through an explicit evaluation-contract version bump.

### Metric and verdict rules

Version the initial evaluation contract independently as `agent-kb-evaluation@1.0.0`. The corpus index assigns stable case identifiers and a partition to every case, declares the coverage matrix, and binds every case and expected output by digest. A contract patch may clarify prose without changing a case or gate; adding compatible coverage requires a minor version; changing an oracle, metric, threshold, partition, or existing case meaning requires a major version.

For each `use_okf` case, required recall is the fraction of `required` concepts selected; an empty required set is invalid for that disposition. `Allowed` selections are relevant but do not enter the recall denominator. Mandatory concepts expected by the case must appear in `required`. A selected concept outside `required` and `allowed` is irrelevant. Attribute legacy bytes to the same profile concept boundaries, exclude common runtime `AGENTS.md` bytes from both sides, and report structural overhead separately. A zero-irrelevance legacy case passes only when OKF also selects zero irrelevant bytes and is excluded from ratio calculations. For the rest, per-case reduction is `1 - okf_irrelevant_bytes / legacy_irrelevant_bytes`; aggregate reduction uses summed bytes, and the median uses the deterministic ordered per-case values.

Run latency measurements in fresh processes on the declared reference CI image, with at least 30 measured executions per promotion case and no hidden warm-up sample. Use monotonic elapsed time around selector invocation, report median, nearest-rank p95, and maximum over all measured executions, and retain raw samples in the CI artifact. Timing failure cannot be waived by faster averages elsewhere.

Promotion is conjunctive and fail closed: corpus/schema/digest validation; every semantic, exact-output, mutation, and provider-parity hard gate; 100% per-case required recall; no recall regression; no per-case irrelevant-byte increase; at least 30% aggregate and 20% median irrelevant-byte reduction; and the latency limits must all pass in one complete same-commit report. Missing, stale, skipped, or internally inconsistent evidence is a failed promotion, never an implicit pass.
