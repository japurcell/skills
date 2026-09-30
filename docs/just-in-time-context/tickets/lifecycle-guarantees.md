# Lifecycle Guarantees

**Type:** grilling
**Status:** closed
**Blocked By:** provider-lifecycle-capabilities.md, success-criteria.md
**Research Dir:** not applicable

## Question

What guarantees must retrieval, learning, and maintenance provide across Codex, Copilot, and Gemini given each provider's actual lifecycle capabilities?

Define task, turn, session, and work-session boundaries; required automatic triggers; completion signals; and any provider-specific fallback. Decide what "does not rely on agents remembering" means in observable behavior. Determine whether a hook invokes work, injects guidance, or enforces a pending-work contract, and which supported surfaces the first version guarantees. Skill subcommands remain a proposed interface.

Apply [Context Retrieval Contract](context-retrieval-contract.md) to startup, scope expansion, compaction, resume, and child execution. Choose automatic events and enforcement that establish delivery before dependent work rather than assuming native discovery or inheritance. The semantic retrieval requirements are settled; provider mechanisms and guarantees remain this ticket's decisions.

---

## Resolution

The user confirms this contract on 2026-09-29 after settling Q1-Q8 and accepting the final shared-understanding confirmation.

### First-version scope and certification

Target Codex desktop, Codex CLI, Copilot CLI, and Gemini CLI. Defer VS Code Local and Copilot Agent Host beyond the first version. Cover fresh interactive sessions, resume and compaction, noninteractive CLI runs, and delegated work launched through supported integrations.

Certify every selected version, configuration, entry mode, and child path separately before claiming support. CLI-to-desktop parity, shared provider names, configuration registration, and presumed inheritance are insufficient proof. Native events or a validated automatic fallback must satisfy the same contract. If neither can do so, declare that path unsupported rather than silently reducing its guarantees. A targeted surface is not already certified by this planning decision.

### Boundaries

A task is the user's objective across clarification turns. A turn is one agent response cycle. A session is the provider conversation/runtime container. A work session ends when the requested task or task batch, including delegated work, finishes. Waiting for the user or ending a response turn does not itself finish the task. Interruptions preserve unfinished obligations.

### Automatic stages and roles

Supported integrations automatically initiate required stages or register obligations that they require to run before dependent work or successful completion. The user does not invoke recall, learning, or maintenance manually. Apply [Context Retrieval Contract](context-retrieval-contract.md) at each relevant boundary.

- Startup and resume deliver the bootstrap contract and detect pending work. Recover at the eligible opportunity defined below.
- Task arrival establishes current scope and retrieves applicable guidance before dependent work.
- Newly dependent work or scope expansion triggers additional retrieval before the governed action or conclusion.
- During work, capture compact candidates when durable lessons emerge. Apply [Knowledge Evidence Policy](knowledge-evidence-policy.md); read-only work can produce lessons without requiring an invented knowledge addition.
- Compaction and resume restore missing relevant context before dependent work, preserving scoped reuse only while guidance remains available, current, and applicable.
- Delegation verifies assigned-scope delivery before child governed work. Missing child events or unverified inheritance do not establish delivery. Include delegated work in work-session completion.
- Work-session completion performs required learning and affected-knowledge refresh, including a verified no-change result when applicable. Do not perform full maintenance on every clarification turn.
- Interruption or termination preserves unfinished obligations and an incomplete outcome. Orderly shutdown may attempt cleanup but does not establish completion.

Distinguish event detection, context delivery, work invocation, and enforcement. A hook may perform deterministic work directly, deliver context, or register an obligation for an automatically invoked agent stage. Injecting instructions alone proves neither semantic source evaluation nor maintenance execution. Required stages must actually run and establish their outcomes before dependent work or successful completion. Concrete component boundaries and provider wiring remain representation decisions.

### Completion and interruption

A stopped provider turn is a lifecycle checkpoint, not proof that the work session completes. Report successful completion only after delegated work and required learning/refresh finish, including verified no-change when applicable. Retain lightweight completion evidence. Apply the quality, recovery, token-volume, and timing gates in [Success Criteria](success-criteria.md).

If a timeout, cancellation, provider continuation cap, or other interruption leaves obligations unfinished, expose an incomplete outcome and preserve recoverable pending work. Never rely on unlimited stop retries. Provider termination does not turn pending obligations into successful completion. Storage, outcome checks, bounded retries, and publication/recovery mechanics remain for [Failure and Concurrency Contract](failure-and-concurrency-contract.md).

### Next eligible opportunity

Detect pending work at the next supported startup, resume, or task event. An opportunity is eligible for recovery when the required access and authorization are available. Recover before affected dependent work or successful completion; independent work may continue under the closed retrieval contract.

Respect explicit pauses and cancellation without restarting a canceled user task. Closed or idle sessions do not promise execution without a validated automatic trigger. Shutdown cleanup is best effort; the recovery guarantee is pending-work detection and recovery at the next eligible event. This decision does not require an unconditional background recovery runner.

### Provider constraints and automatic fallbacks

The closed [Provider Lifecycle Capabilities](provider-lifecycle-capabilities.md) and its [findings](../research/provider-lifecycle-capabilities/findings.md) establish documented constraints, not deployed certification. Codex context injection and asynchronous hooks do not guarantee an idle semantic turn; desktop parity needs its own proof. Copilot limits consecutive stop continuations to eight, excludes some child paths from child hooks, and limits its startup prompt-hook invocation to new interactive sessions. Gemini compression and shutdown hooks are advisory, and child inheritance and deployed final-response retry require proof. These limits prevent treating one provider's event as a universal mechanism.

Allow an automatic adapter or supervised execution path where native events cannot fulfill the contract, including noninteractive and child paths. Validate the fallback against the exact version, configuration, and mode. It must preserve retrieval, learning, completion, and recovery requirements without manual lifecycle invocation. An unavailable or unvalidated path cannot be advertised as supported. Detailed fallback packaging and setup remain later decisions.

### Remaining decisions and verification

[Context Organization and Skill Boundary](context-organization-and-skill-boundary.md) selects representation, component ownership, skill packaging, and concrete provider integration. [Maintenance Scheduling and Pruning](maintenance-scheduling-and-pruning.md) selects periodic consolidation/pruning timing, execution when no agent session is active, and how due work joins this lifecycle. [Failure and Concurrency Contract](failure-and-concurrency-contract.md) selects durable ownership, duplicate handling, retries, cancellation, and recovery mechanisms. [Adoption and Validation Contract](adoption-and-validation-contract.md) selects deployed versions, capability probes, concrete workloads, instrumentation, setup, and rollback proof.

No provider probe, background runner, hook configuration, or product implementation is created in this decision session. The provider briefing reuses completed research; no new live guarantee or acceptance measurement is established.
