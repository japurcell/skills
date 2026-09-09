# Dual-Provider Evaluation Amendment

**Type:** grilling
**Status:** obsolete
**Blocked By:** none
**Research Dir:** N/A

## Question

How should the existing evaluation contract be amended to qualify the Copilot project extension and Gemini adapter, require exact provider-neutral parity while distinguishing `advisory_stop` from `hard_stop`, test experimental-extension lifecycle and failure behavior, and produce independent provider promotion verdicts without weakening recall, determinism, efficiency, latency, or privacy gates?

---

<!-- Resolution will be appended here -->

## Accepted round 1

- Retain the provider-neutral corpus as the single semantic source of truth. Run shared selector and runtime cases once, publish replay vectors for both adapters, and use separate provider suites only for envelopes, lifecycle, enforcement, and host integration. Version the amended contract as `agent-kb-evaluation@2.0.0`; preserve v1 fixtures and results, but do not accept v1 evidence for provider enrollment.
- Emit independent `shared_core`, `copilot`, and `gemini` verdicts. A provider passes only when the shared verdict and its own verdict pass. Both adapters must exist and be evaluated before the first promotion; a provider-specific failure blocks only that provider, while a shared-core failure blocks both.
- Require byte-identical provider-neutral request normalization, disposition basis, selected logical paths and order, rendered OKF or legacy context, lifecycle substitutions, reason codes, and privacy-safe audit fields. Compare provider envelopes through explicit semantic oracles: Copilot `advisory_stop` plus tool denial and Gemini `hard_stop` are required provider differences, not parity failures.
- Bind qualification evidence to the exact CLI build, adapter digest, evaluation-contract digest, and platform identity for each provider. A new CLI build requires new committed evidence. Runtime capability checks detect drift but never replace build-matched qualification.
- Make startup, prompt submission, concurrent or steered prompts, stale-completion suppression, final-response events, `/clear`, resume, workspace changes, reload, session end, child cleanup, timeouts, malformed protocol output, handler exceptions, latch recovery, unavailable experimental support, and observability failures hard provider-suite coverage. Each case asserts context cardinality, tool state, continuation bounds, disposition, and absence of sensitive diagnostic data.
- Preserve the selector's p95-at-or-below-100-ms and maximum-at-or-below-250-ms gates. Add separate hard gates for clean-state reconciliation plus full runtime invocation and adapter overhead, with thresholds fixed from development measurements before promotion. Test contention and fault paths against the production timeout separately so exceptional waits do not dilute normal-path latency results.

## Accepted round 2

- Require two complementary test layers. Deterministic shared-runtime and adapter-harness tests run on every relevant change; promotion additionally requires behavioral tests inside each exact Copilot and Gemini CLI build. Simulated adapters cannot qualify undocumented host lifecycle behavior.
- Qualify every declared deployment tuple independently by provider CLI build, operating system, architecture, runtime versions, and adapter digest. Run shared-core tests on every supported platform, and never use evidence from one tuple to qualify another.
- Commit a compact machine-readable qualification manifest containing bound identities and digests, verdicts, thresholds, test counts, and immutable CI-artifact references. Retain complete reports and sanitized logs as CI artifacts. Enrollment validates the committed manifest; absent required supporting evidence fails qualification.
- Prove the privacy gate with synthetic sentinels placed in prompts, concepts, absolute paths, environment values, and malformed subprocess payloads. Scan adapter output, stdout, bounded stderr, reports, and observability records for sentinel values and forbidden fields. Any occurrence is a zero-tolerance provider failure.
- On the reference CI environment, require clean-state reconciliation plus runtime invocation to remain at p95 at or below 500 ms and maximum at or below 1,000 ms over at least 30 cold executions per promotion case. Measure adapter overhead separately, excluding host scheduling, with p95 at or below 50 ms and maximum at or below 100 ms. Bound the complete subprocess at two seconds; lock acquisition and cleanup must fit inside that timeout. Contention and timeout cases assert the correct unsafe disposition and child reaping outside clean-path percentiles.

## Accepted round 3

- Preserve optional task-kind and repository-path cases for direct selector coverage, but restrict the provider promotion partition to deployed inputs: current submitted prompt, validated workspace identity, one stable UTC timestamp, and configured task scope. Provider recall must pass without inferred task kind, repository paths, conversation history, Git state, environment data, or filesystem enumeration.
- Never grade nondeterministic model prose. Exercise the exact production adapter with a qualification fixture that records only privacy-safe event codes, context digests, dispositions, tool decisions, continuation counts, and timings. Verify exact context bytes in the deterministic adapter harness; use live CLI tests to verify adapter loading, callback order, tool denial, reset behavior, and cleanup against those digests.
- Promotion CI must verify that referenced supporting artifacts exist and match their digests before committing qualification evidence. Runtime enrollment validates only the committed local manifest and never requires network access. Later CI-artifact expiration does not disable an already qualified offline checkout.
- Give every provider and shared-core run a `pass`, `fail`, or `incomplete` verdict. A behavioral mismatch is `fail`; unavailable infrastructure or an aborted run is `incomplete`; neither permits promotion. Do not conceal either through automatic retries. A deliberate rerun creates a new immutable report linked to the prior attempt.
- Keep UTF-8 bytes as the relevance and efficiency gate and continue reporting provider-native prompt-token counts without gating on them. Record same-platform legacy latency for comparison, but apply the accepted absolute latency limits because the old hook and replacement adapter paths are not structurally equivalent.
- Invalidate both provider verdicts when the shared runtime, profile, projection, selector, producer, corpus, oracle, evaluation contract, thresholds, or shared dependencies change. Invalidate only the affected deployment tuple when its adapter, provider envelope, CLI build, runtime version, operating system, or architecture changes. Prose-only changes that leave all bound digests unchanged do not invalidate evidence.

## Final confirmation

The user confirmed the complete three-round contract without further changes.

## Resolution

Replace the provider-parity portion of `agent-kb-evaluation@1.0.0` with `agent-kb-evaluation@2.0.0` while preserving the original fixtures and historical results. Keep one provider-neutral semantic corpus and shared-core verdict, then derive deterministic replay vectors and separate Copilot and Gemini provider suites. Both adapters must exist and be evaluated before the first promotion. A provider qualifies only when `shared_core` and its own provider verdict pass; a shared failure blocks both providers, while a provider-specific failure blocks only that provider.

Require byte-identical normalized requests, disposition basis, selected logical paths and order, rendered OKF or legacy context, lifecycle substitutions, reason codes, and privacy-safe audit fields across adapters. Treat Copilot `advisory_stop` plus deny-all-tools and Gemini `hard_stop`, along with their documented envelopes and injection mechanics, as explicit semantic-oracle differences. Provider promotion cases use only fields available in deployment: current submitted prompt, validated workspace identity, one stable UTC timestamp, and configured task scope. Direct selector coverage may exercise optional task kind and repository paths, but provider recall cannot depend on inferred prompt, conversation, Git, environment, or filesystem metadata.

Combine deterministic shared-runtime and adapter-harness tests on every relevant change with live behavioral qualification inside each exact provider CLI build. Bind qualification to the CLI build, adapter and contract digests, operating system, architecture, runtime versions, and platform identity; qualify each deployment tuple independently. Verify exact context bytes in the harness and use the exact production adapter plus a privacy-safe qualification fixture to observe only event codes, context digests, dispositions, tool decisions, continuation counts, and timings in the live host. Never grade model prose.

Make all accepted startup, prompt, concurrency, steering, stop, reset, reload, workspace, shutdown, child-process, protocol, timeout, capability, handler, latch-recovery, and observability cases hard gates. Assert exact context cardinality, disposition, tool state, continuation bounds, stale-completion suppression, and cleanup. Seed synthetic sentinels into every forbidden data class and fail the affected provider if any sentinel or forbidden field reaches adapter output, stdout, bounded stderr, reports, or observability.

Commit a compact machine-readable qualification manifest containing all bound identities and digests, thresholds, test counts, verdicts, and immutable CI-artifact references. Promotion CI verifies artifact existence and digests before committing that manifest. Runtime enrollment validates only committed local evidence and performs no network access; later artifact expiration does not break an already qualified offline checkout. Classify every run as `pass`, `fail`, or `incomplete`; only `pass` permits promotion. Do not mask failures or incomplete infrastructure with automatic retries, and retain deliberate reruns as new immutable reports linked to earlier attempts.

Preserve every v1 semantic, mutation, recall, determinism, irrelevant-byte, and selector-latency gate. Continue using UTF-8 bytes for relevance and efficiency, report provider-native prompt tokens without gating, and report same-platform legacy latency without treating structurally different paths as equivalent. Retain selector p95 at or below 100 ms and maximum at or below 250 ms. On the reference CI environment, measure at least 30 cold executions per promotion case and require clean reconciliation plus full runtime invocation at p95 at or below 500 ms and maximum at or below 1,000 ms; require adapter overhead, excluding host scheduling, at p95 at or below 50 ms and maximum at or below 100 ms. Bound the complete subprocess at two seconds, including lock acquisition and cleanup, and evaluate contention and fault outcomes separately from clean-path percentiles.

Invalidate both provider verdicts for changes to the shared runtime, profile, projection, selector, producer, corpus, oracle, evaluation contract, thresholds, or shared dependencies. Invalidate only the affected deployment tuple for changes to its adapter, provider envelope, CLI build, runtime version, operating system, or architecture. Prose-only changes that leave all bound digests unchanged do not invalidate qualification.
