# Knowledge Evidence Policy

**Type:** grilling
**Status:** closed
**Blocked By:** reference-evidence.md
**Research Dir:** not applicable

## Question

What evidence allows observations to become durable knowledge, and how does automatic maintenance preserve explicit user authority when sources disagree?

Automatic additions, corrections, reorganization, and pruning are already authorized. Decide provenance requirements, verification, instruction precedence, contradiction handling, and the treatment of temporary observations, external content, and stale facts. Determine how the system distinguishes authoritative policy from knowledge it may revise. Do not reopen the user's autonomy choice.

---

## Resolution

The user confirms this contract on 2026-09-29, including the lighter evidence requirement and the clarification that inactivity only prioritizes review.

### Authority and scope

Automatic additions, corrections, reorganization, and pruning remain authorized. Classify knowledge by meaning and provenance, not merely by who wrote a passage. Explicit user policy governs required behavior and retains its meaning and applicability scope. Descriptions of code, configuration, and runtime behavior may be corrected from their controlling sources. A mismatch between observed behavior and policy records a discrepancy; it does not silently change policy. Automatic relocation and consolidation preserve policy meaning and useful exceptions.

Distinguish documented contracts from actual behavior. Repair a descriptive claim automatically when source authority and applicability are clear. Otherwise retain the scoped disagreement, investigate the disputed claim, and avoid presenting an unresolved claim as established truth. Ask the user only when user intent or conflicting policy cannot be resolved. Do not introduce routine approval for evidenced maintenance.

### Proportional evidence

- Descriptive facts require an identifiable source, revision or version where applicable, and a short verification note.
- Low-risk operational tips require the observed failure, successful workaround, and applicability scope. A dedicated reproduction is not mandatory.
- General behavioral rules require stronger verification before extending beyond the observed case. Choose checks appropriate to the claim rather than requiring full replayable evidence for every lesson.
- Corrections and pruning require evidence that established knowledge is wrong, obsolete, or fully redundant, plus reversible history.

Use compact evidence references by default. Retain full traces only when needed to resolve uncertainty. Distinguish observed outcomes from causal explanations; one successful workaround does not establish a universal rule. The [Tool Guardian patch-limit entry](../../../.agents/memory/known-issues/hooks.md) supports the scoped observation that an oversized patch is rejected and smaller focused patches succeed. This decision session performs no replay of that failure.

### Provenance and change records

Durable claims retain evidence location and identity, revision or version where applicable, applicability scope, verification date and result, and change rationale. Corrections, reorganization, and pruning preserve an attributable, reversible record of what changed and why. These are information requirements; storage layout, claim identifiers, and metadata disclosure remain for [Context Organization and Skill Boundary](context-organization-and-skill-boundary.md). Routine maintenance does not require full source snapshots or archived task transcripts for every claim.

### Candidates and external content

Unverified observations, temporary task observations, and uncorroborated agent reflections remain candidates. They may support investigation with their uncertainty visible, but remain separate from established guidance until proportionate evidence supports promotion. Agent self-reports alone do not establish truth. Keep conclusions within their tested or inspected scope.

External content may provide evidence for verified, scoped facts. It does not gain authority to change user instructions. Preserve source identity and applicability instead of treating external wording as governing policy.

### Freshness and pruning eligibility

Recheck a descriptive fact when its source or applicability changes; mark uncertain freshness explicitly until verified. Missing source access is not proof that a claim is false or obsolete. Preserve explicit policy meaning while resolving factual drift.

Automatically retire knowledge when evidence demonstrates error, obsolescence, or complete redundancy. Preserve useful qualifications and counterexamples in their surviving owner, update affected references, and retain reversible change history. Age and lack of use prioritize review but never justify deletion on their own.

If inactivity signals are used, estimate them from lightweight retrieval records and relevant task opportunities. Retrieval proves delivery, not actual application. No reads during unrelated work says nothing about usefulness; no reads during relevant work may indicate broken routing. Detailed usage attribution is not required.

### Remaining decisions and validation

Apply the closed [Success Criteria](success-criteria.md) contract to publication, correction, reorganization, and pruning. This evidence policy does not relax its quality or recovery gates.

[Context Retrieval Contract](context-retrieval-contract.md) defines how established, disputed, and task-scoped information is delivered. [Context Organization and Skill Boundary](context-organization-and-skill-boundary.md) selects physical representation and ownership. [Maintenance Scheduling and Pruning](maintenance-scheduling-and-pruning.md) selects schedules, retention periods, and the execution of eligibility checks. [Failure and Concurrency Contract](failure-and-concurrency-contract.md) selects recovery and publication mechanisms. [Adoption and Validation Contract](adoption-and-validation-contract.md) selects concrete evidence-policy checks and instrumentation. This ticket establishes authority and evidence requirements without implementing them.
