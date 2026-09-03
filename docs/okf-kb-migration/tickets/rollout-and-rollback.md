# Rollout and Rollback

**Type:** grilling
**Status:** claimed by subagent-k7m2q9
**Blocked By:** provider-integration-and-state.md, evaluation-corpus-and-promotion-gates.md
**Research Dir:** N/A

## Question

What phased rollout, shadow-mode comparison, opt-in/default promotion sequence, diagnostics, failure containment, rollback trigger, and legacy-loader retirement criteria make the migration reversible and observable?

---

<!-- Resolution will be appended here -->

## Resolution

### Accepted round 1

- Roll Gemini through `shadow`, `canary`, and `default` independently. Keep ordinary Copilot CLI on `legacy` until current official documentation and behavioral tests prove a true pre-model denial, unambiguous current-prompt identity, trustworthy workspace and event-time inputs, valid JSON-only responses, and privacy-safe payload handling. If Copilot later passes those capability gates, it starts its own rollout ladder at `shadow`; it never inherits Gemini's promotion state. A standalone Copilot SDK wrapper is a possible separate effort, not part of this migration.
- In `shadow`, always serve legacy context while computing OKF results read-only for comparison. Record only approved privacy-safe contract metadata; never inject candidate context or let an OKF-only failure disrupt the turn. Existing source-ingest safety gates remain enforced.
- Refine the unreleased `agent-kb-runtime@1.0.0` contract with an explicit per-provider mode of `legacy`, `shadow`, `canary`, or `default`. Configuration changes are reviewed repository commits; do not add environment-variable or hidden per-user overrides. Copilot rejects any mode beyond `legacy` until its capability gate passes.
- Use designated canary branches or worktrees with committed candidate configuration rather than silent user bucketing. Participants knowingly exercise normal tasks while rollback remains one configuration revert away.
- In addition to the complete same-commit CI promotion gates, require one full normal work cycle and at least 50 eligible prompt invocations, whichever takes longer, with no safety, parity, or fallback-class regression. Any candidate or runtime-configuration change restarts the evidence window.

The supporting 2026-09-03 official-source assessment is in [`../research/copilot-cli-hooks-rollout.md`](../research/copilot-cli-hooks-rollout.md).

### Accepted round 2

- Immediately return an enrolled provider to `legacy` after any injected invalid or stale context, missing mandatory context, forbidden lifecycle content, mixed OKF and legacy context, provider divergence, nondeterminism, privacy leakage, or incorrect safety disposition. Expected per-invocation `use_legacy` and `hard_stop` results are not rollout failures by themselves.
- When no safety invariant is violated, elevated fallback or latency freezes promotion and triggers investigation. Roll back only when the canary exceeds a predeclared operational envelope derived from shadow evidence for a complete rolling 50-eligible-prompt window; do not impose one workload-independent fallback rate.
- Roll back with one minimal reviewed configuration change that sets the affected provider to `legacy`; never delete the projection or mutate canonical documents. A shared-runtime or projection defect rolls every enrolled provider back, while an adapter-only defect rolls back only that provider.
- Runtime code remains read-only and never changes rollout state. It continues to apply the closed per-invocation fallback and hard-stop matrix; a maintainer performs deployment rollback through version control so the cause, commit, and configuration digest remain auditable.
- A corrected release never skips stages. Re-promotion requires a documented root cause, regression coverage, a complete new exact-commit CI report, and a fresh `shadow` to `canary` to `default` sequence with a restarted evidence window.

### Accepted round 3

- Derive and freeze each provider's canary operational envelope from that provider's completed shadow window. Cover unexpected fallback and hard-stop rates, adapter errors, provider-envelope failures, and latency; safety invariants remain zero-tolerance outside any statistical envelope.
- Keep privacy-safe per-event records in existing provider observability storage. Each promotion pull request records the CI run, candidate commit, contract/configuration/projection digests, frozen operational envelope, eligible invocation count, observation period, and aggregate results. Never commit prompt-level logs, task text, rendered context, lexical evidence, or concept bodies.
- Permit only forward `legacy` to `shadow` to `canary` to `default` transitions, plus immediate rollback from any mode to `legacy`. A changed candidate begins again at `shadow`. CI rejects skipped forward transitions or missing evidence; runtime validates only the current configuration and never attempts to reconstruct or enforce deployment history.
- Do not retire the legacy loader during this migration. Copilot still requires it, and the closed failure matrix depends on it for atomic fallback; initial rollout completion therefore cannot imply retirement.
- Consider retirement only as a separate major-contract effort after every supported provider is safely at `default`, no supported path depends on `use_legacy`, every fallback class has an equally safe replacement, older-checkout compatibility is addressed, and complete new promotion evidence validates the replacement. Elapsed time alone is never sufficient.
