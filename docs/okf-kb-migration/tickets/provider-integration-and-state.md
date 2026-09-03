# Provider Integration and State

**Type:** grilling
**Status:** closed
**Blocked By:** projection-producer-and-linter.md, mandatory-context-and-fallback.md
**Research Dir:** N/A

## Question

Where does the shared OKF producer/consumer boundary sit relative to Copilot and Gemini adapters, how are repo and installed assets located, how is state versioned and migrated, and how do prompt timing, JSON-only stdout, final-response gates, error handling, and provider parity remain intact?

---

<!-- Resolution will be appended here -->

## Resolution

Adopt a provider-neutral runtime boundary around the closed selector contract. One shared core validates normalized requests, projection integrity, selection, audit data, and disposition. Thin repository-owned Copilot and Gemini adapters locate the active workspace, establish source-ingest safety, construct the provider-neutral request, invoke the read-only core, run the shared deterministic legacy loader when directed, and translate the result into provider-specific JSON. The producer remains an explicit contributor/CI operation and is never invoked by startup, prompt, final-response, selector, or adapter paths.

### Invocation and context

Run selection once per eligible prompt event: Gemini `BeforeAgent` and, only after its safety capability gap is resolved, Copilot `userPromptTransformed`. Because Copilot may deliver the prompt event before `sessionStart`, every prompt path must reconcile current source-ingest state before selection. Startup reconciliation remains, and final-response hooks reconcile source-ingest state again without rerunning selection. The operational reconciliation may update source-ingest manifest v1 under its existing lock; the selector and committed projection remain read-only.

For `use_okf`, inject one clearly delimited rendered-context block before the untouched task. Copilot uses `modifiedTransformedPrompt`; Gemini uses `hookSpecificOutput.additionalContext`. Never inject candidate audits or diagnostics, and never mix OKF and legacy context. For `use_legacy`, discard all OKF output and have the shared compatibility loader follow the existing `AGENTS.md` plus `.agents/memory/INDEX.md` path before the adapter constructs its envelope.

Capture one normalized RFC 3339 UTC event timestamp per prompt invocation and reuse it through retries and audit output. Production adapters use the validated provider event time where available, otherwise one injected adapter clock reading; tests always inject the clock.

### Inputs and runtime configuration

Add one committed provider-neutral `.agents/okf-runtime.json` governed by `agent-kb-runtime@1.0.0`. It supplies the positive UTF-8 byte budget, positive concept limit, and conservative default `task-scope: nontrivial`. Both adapters read the same configuration; provider hook declarations contain no duplicated policy values. Missing configuration means OKF integration is disabled and existing legacy behavior continues. Once enabled, malformed or unsupported configuration is unsafe caller state and causes `hard_stop`; runtime code never creates, repairs, or migrates it.

Do not guess production budget values during design. Implementation evaluates a bounded set of budget pairs against the frozen promotion corpus and commits the smallest pair passing every safety, recall, parity, latency, and efficiency gate, breaking ties by lower byte budget and then lower concept limit. A budget change requires complete promotion evidence and a new configuration digest, not a schema-version bump.

When validated structured caller metadata supplies `task-scope`, `task-kind`, or repository-relative paths, pass it through after contract validation. Otherwise use `nontrivial`, omit task kind, and pass an empty path list. Never derive these values from task prose, conversation state, Git state, directory enumeration, or the process working directory.

### Asset and state boundaries

Resolve project knowledge only from a validated active-workspace root supplied by the provider. Repository-owned adapters under the active checkout consume that checkout's `.agents/okf/`, `.agents/okf-runtime.json`, or legacy `.agents/memory/INDEX.md`. Globally installed hooks remain generic observability, security, and skill-loading infrastructure; they never search home directories, parent repositories, or adjacent workspaces for project KB content. A repository with no runtime configuration is unenrolled and receives no OKF adapter injection.

Keep source-ingest manifest v1, projection manifest v1, runtime configuration, and provider-local observability databases as independent state contracts. Prompt-time code silently migrates none of them. Record the runtime schema version and configuration digest in adapter audit results and promotion evidence. Runtime-contract patch releases may clarify diagnostics without observable changes; minor releases may add optional fields or provider capabilities while preserving behavior; changes to input acquisition, default-scope meaning, disposition mapping, context composition, or configuration semantics require a major release.

### Dispositions, concurrency, and final gates

Apply this closed adapter matrix:

- no runtime configuration: leave existing legacy behavior unchanged;
- valid selection: `use_okf`;
- missing, invalid, stale, or incompatible projection; selector failure; `no_match`; or mandatory budget exhaustion: discard partial output and `use_legacy`;
- malformed or unsafe input, unreadable or indeterminate source-ingest state, pending ingest, access violation, invalid enabled runtime configuration, failed legacy loading, or an unexpected failure before safety state is established: `hard_stop`.

Never return `{}` for an enrolled request after an unsafe failure. Reconcile source state under the existing manifest lock, release it, then validate and select from one projection-manifest snapshot. Do not hold the source lock during selection. At the final hook, reconcile only source-ingest state: pending or indeterminate state blocks or halts the response, while projection changes are handled on the next prompt.

### Provider enforcement and parity

Gemini `BeforeAgent` can enforce `hard_stop` with a turn denial, and `AfterAgent` remains its final-response gate. Current Copilot prompt hooks cannot satisfy the same contract: `userPromptTransformed` is mutation-only, fires for the primary and preceding batched messages without an unambiguous current-message discriminator, and `agentStop` or `subagentStop` can only force bounded continuation. Do not weaken `hard_stop` into prompt instructions or stop-hook retries. Keep Copilot on its legacy path and withhold OKF promotion until tested host capabilities provide pre-turn denial, unambiguous current-prompt identification, trustworthy workspace and event-time fields, and provider-valid JSON responses. Detect capabilities behaviorally rather than trusting a CLI version string. Provider-specific rollout timing belongs to **Rollout and Rollback**.

Emit exactly one provider-valid JSON object followed by one newline on stdout. Send only privacy-safe diagnostics to stderr or existing observability paths: contract versions and digests, disposition, reason codes, timings, counts, and logical paths. Never record task text, concept bodies, rendered context, or lexical evidence.

Given identical normalized requests and projections, adapters must produce byte-identical provider-neutral dispositions, rendered context, ordering, reason codes, counts, lifecycle substitutions, and audit data. Provider envelopes may differ only as documented, with snapshot tests proving semantic equivalence. Copilot `hard_stop` replay remains an expected capability failure that blocks its promotion until the host contract changes.
