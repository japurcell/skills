# Context Retrieval Contract

**Type:** grilling
**Status:** closed
**Blocked By:** provider-lifecycle-capabilities.md, reference-evidence.md, knowledge-evidence-policy.md
**Research Dir:** not applicable

## Question

What context must an agent receive, and what task information determines when additional knowledge becomes relevant?

Define always-present guidance, task-scoped knowledge, lookup units, relevance signals, completeness checks, and changes of task or file scope. Decide how retrieval works before a task is known and after scope expands, including non-editing work. Specify the observable contract independently of a particular file layout or skill name.

Use [Reference Evidence](reference-evidence.md) to distinguish provider discovery rules, filenames, CWD-based loading, and tool-triggered loading. Include compaction and child-agent context propagation rather than assuming inherited knowledge.

Apply [Knowledge Evidence Policy](knowledge-evidence-policy.md) when defining delivery of established guidance, uncertain freshness, disputed facts, and candidates available for investigation. Preserve the distinction between delivery and demonstrated application without requiring detailed usage attribution.

---

## Resolution

The user confirms this contract on 2026-09-29 after accepting Q1-Q7 and the final shared-understanding confirmation.

### Startup and authority

Before a task is known, provide applicable user/global instructions, universally applicable repository policy, a compact knowledge map, and the retrieval procedure. Deliver conditional guidance before the action it governs. Preserve explicit loading requirements and their ordering; context optimization does not authorize weakening them. Every repository's applicable instructions retain their authority.

The startup map must let the agent discover relevant guidance without preloading every area guide or knowledge entry. When the task becomes known, retrieve its additional context before dependent work.

### Relevance and delivery timing

Determine relevance from task intent, planned action, affected files, concepts, dependencies, and provider/runtime scope. File paths are one signal, not the entire contract. Retrieval covers read-only investigation and conclusions as well as edits.

Deliver relevant guidance before the first action or conclusion that depends on it. Reevaluate when the task changes, file or conceptual scope expands, a dependency introduces another affected area, or new evidence changes applicability. If relevance is uncertain, inspect the relevant routing information and broaden the lookup. This does not require repeating an unchanged lookup before every tool call.

### Guidance units and sources

Deliver the smallest self-contained guidance unit that preserves meaning. Include applicability, important exceptions, and required linked guidance; follow required dependencies rather than returning an isolated fragment. Explicit requirements to read a complete artifact remain in force.

Keep source references available. Inspect controlling sources when precision, freshness, or an explicit repository requirement calls for them. A summary can route investigation without establishing exact current behavior. Lookup units are a semantic requirement; file layout, identifiers, indexing, and retrieval mechanism remain open.

### Established and uncertain knowledge

Apply [Knowledge Evidence Policy](knowledge-evidence-policy.md). Deliver applicable established guidance first. Surface freshness uncertainty and unresolved conflicts when they affect the task, and verify facts before relying on them. Preserve explicit policy while investigating factual disagreement.

Candidates appear only when relevant to investigation and remain clearly unverified. External material may supply evidence but gains no instruction authority. Do not present unresolved or candidate claims as established guidance. Evidence requirements remain proportional to the claim.

### Scoped completeness and missing context

Before dependent work, check the current task scope against applicable mandatory guidance and required references. Confirm complete delivery; expose missing content or incomplete output and broaden lookup when needed. This checks known obligations, not every potentially useful fact or an exhaustive search of the knowledge base.

Retain lightweight delivery information sufficient to verify relevant content was available before governed work and to expose delivery gaps. Delivery does not demonstrate application. Detailed usage attribution is unnecessary. The behavior and artifact checks in [Success Criteria](success-criteria.md) remain required; agent self-reports alone do not establish correctness.

When required context is unavailable, attempt focused search and authoritative fallback automatically. A fallback must preserve the authority and applicability of the needed guidance. Continue independent work, but pause the action that depends on missing policy or a material unresolved fact. A qualified factual answer may proceed when uncertainty can be stated accurately. Failed retrieval never establishes that no guidance applies.

Ask the user only about unresolved intent or policy, or missing input that cannot be recovered. This contract defines the affected-action boundary; retry mechanics, recovery ownership, and durable failure records remain later decisions.

### Compaction, resume, and delegation

Every executing agent receives the startup contract and guidance relevant to its assigned scope before governed work. Verify child-agent delivery rather than assuming inherited knowledge. Compaction and resume require restoring missing context before dependent work.

Reuse delivered guidance only while it remains available, current, and applicable. Retrieve again when scope or relevant knowledge changes. A prior delivery record does not prove the content remains in the active context. Provider discovery, CWD loading, nested files, and tool-triggered loading have different documented behavior; none is a universal delivery guarantee.

### Concrete repository illustrations

A narrow read-only question about the recorded patch limit can start at the [Tool Guardian KB entry](../../../.agents/memory/known-issues/hooks.md), under the read-only orientation policy in [AGENTS.md](../../../AGENTS.md). It does not require loading every architecture and area guide. A question about exact current guard behavior requires appropriate controlling-source inspection; the recorded tool rejection alone does not establish attribution to a repository hook.

A nontrivial source auto-ingest edit retains the root policy's INDEX, architecture, conventions, and affected-area prerequisites. [Hook guidance](../../../.agents/instructions/hooks.md) routes the affected subsystem to [Auto-ingest guidance](../../../.agents/instructions/hooks-auto-ingest.md) and its matching known-issues/testing documents. A newly affected area expands the required context before work in that area. These illustrations describe existing policy; they do not certify automatic retrieval or select the acceptance workload.

### Remaining decisions

[Lifecycle Guarantees](lifecycle-guarantees.md) selects supported surfaces, event boundaries, automatic triggers, and enforcement. [Context Organization and Skill Boundary](context-organization-and-skill-boundary.md) selects representation and component ownership. [Failure and Concurrency Contract](failure-and-concurrency-contract.md) selects recovery and concurrency mechanisms within this retrieval contract. [Adoption and Validation Contract](adoption-and-validation-contract.md) selects concrete workloads, instrumentation, and deployed-version checks.

Preserve the accepted quality, context-volume, and latency targets. No retrieval implementation, provider probe, or acceptance measurement is performed in this decision session.
