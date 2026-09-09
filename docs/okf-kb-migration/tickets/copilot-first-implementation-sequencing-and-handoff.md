# Copilot-First Implementation Sequencing and Handoff

**Type:** grilling
**Status:** closed
**Blocked By:** copilot-first-rollout-and-rollback.md
**Research Dir:** N/A

## Question

How should the revised design be delivered as dependency-ordered acceptance gates with explicit path ownership, stable validation commands, documentation obligations, atomic commits, rollback checkpoints, Copilot-first promotion, full Gemini support, and an implementation ExecPlan-ready handoff whose completion criterion is Copilot `default`?

---

<!-- Resolution will be appended here -->

## Accepted round 1

- Use a ten-gate critical path: canonical Source Summary readiness; profile, producer, and deterministic projection; evaluation v2 corpus, oracles, and legacy baseline; shared selector, runtime, protocol, and fallback; both provider adapters plus deterministic harnesses without production cutover; live-host qualification and `legacy` enrollment; atomic cross-provider retirement of the dedicated source-ingest hooks with replacement-adapter legacy verification; then Copilot `shadow`, `canary`, and `default` as three separate gates.
- After the cross-provider cutover, allow Gemini to advance independently through its own `shadow`, `canary`, and `default` ladder. The implementation ExecPlan delivers both qualified adapters and the complete Gemini promotion path, but Copilot reaching `default` completes this migration. The final handoff must record Gemini's current mode, evidence window, and next eligible transition.
- Give every gate one owner with exclusive control of its implementation, tests, generated artifacts, and accompanying documentation, with explicit sequential ownership transfers and an independent acceptance reviewer. Gate 7 has one cross-provider owner so hook retirement remains atomic; shared runtime, evaluation, generated projection, and rollout configuration paths never have concurrent writers.
- Land each accepted build gate as one atomic commit, make Copilot promotion gates configuration-only commits, and commit qualification evidence separately from the adapter implementation it qualifies. Revert defective build or cutover commits as units; deployed rollback uses the accepted reviewed configuration change directly to `legacy`, never runtime mutation or canonical-document repair.

## Accepted round 2

- Assign concrete path groups by gate. Gate 1 owns the canonical Source Summaries, `.agents/memory/INDEX.md`, and source-ingest manifest. Gate 2 owns `.agents/okf-profile.json`, projection producer modules and tests, the public projection entry point, and generated `.agents/okf/`. Gate 3 owns the evaluation v2 corpus, oracles, fixtures, baseline, and evaluation modules. Gate 4 owns the shared selector, runtime, protocol, fallback modules, and tests. Gate 5 owns `.github/extensions/agent-kb/extension.mjs`, the Gemini adapter under `.gemini/hooks/scripts/`, provider harnesses, and their tests. Gate 6 owns the public evaluator, promotion CI, `.agents/okf-qualification/`, and `.agents/okf-runtime.json`. Gate 7 owns both providers' source-ingest registrations, retired scripts, replacement-adapter legacy tests, and any required runtime-configuration change. Gates 8 through 10 own only `.agents/okf-runtime.json`. Shared `scripts/agent_kb/` ownership transfers sequentially; provider adapters never duplicate shared policy.
- Store one compact exact deployment-tuple manifest at `.agents/okf-qualification/<provider>/<tuple-digest>.json`. Each manifest contains its bound `shared_core` and provider verdicts, identities, thresholds, test counts, and immutable artifact references. `.agents/okf-runtime.json` selects it by repository-relative path and SHA-256 digest; there is no mutable `current` manifest.
- Keep four stable public acceptance commands: `python3 scripts/okf-projection.py generate`, `python3 scripts/okf-projection.py check`, `python3 -m unittest discover -s scripts/tests/agent_kb -p 'test_*.py'`, and `python3 scripts/agent-kb-evaluate.py --partition promotion --provider all --format json`. The one evaluator accepts deployment-tuple input for live-host qualification and emits independent `shared_core`, `copilot`, and `gemini` verdicts. Applicable existing hook, startup, observability, installer, shell-syntax, Python-compilation, and `git diff --check` checks remain cumulative; add no general build command or dependency.
- Gates 1 through 7 update affected instructions, memory maps, testing guidance, known issues, API documentation, and user-facing setup documentation in the same atomic commit, followed by one mandatory end-of-session `update-agent-docs` pass. Copilot promotion commits remain configuration-only; detailed evidence stays in CI artifacts and review records. The final migration handoff records Copilot completion and Gemini's exact continuation state.

## Accepted round 3

- Make gates 1 through 4 cumulative acceptance boundaries. Gate 1 requires all nine canonical summaries to parse, all manifest entries to be active with matching live hashes, immutable raw-source hashes, and passing Copilot/Gemini ingest parity while legacy loading remains authoritative. Gate 2 requires strict validation of all 42 concepts, byte-identical repeated generation, a clean read-only check, stable negative diagnostics, atomic publication, and no runtime projection writes. Gate 3 freezes evaluation v2 partitions, digests, same-revision legacy baseline, mutations, deployed-input cases, and human-reviewed oracles before optimization. Gate 4 proves ranking, mandatory closure, budgets, protocol and lifecycle faults, provider-specific unsafe mappings, atomic fallback, determinism, privacy, and latency without mixed context. Never weaken an oracle to admit an implementation.
- Gate 5 requires byte-exact shared results through both deterministic adapter harnesses and correct provider envelope and lifecycle behavior while the existing source-ingest hooks remain active. Gate 6 requires `pass` for `shared_core`, Copilot, and Gemini on every declared deployment tuple, verified manifests and artifacts, and both providers enrolled in `legacy`; any `fail` or `incomplete` stops progress. Gate 7 uses one cross-provider commit to remove both dedicated source-ingest registrations and scripts only after qualification, then proves exactly one replacement context path, safe legacy behavior, installer correctness, and no duplicate injection. Never partially retire one provider's compatibility hooks.
- Require every Copilot promotion gate to preserve candidate and deployment-tuple bindings, pass complete exact-commit CI, complete the accepted observation window, retain zero safety and privacy violations, and satisfy the applicable frozen envelope. A shared defect returns every enrolled provider to `legacy`; a provider defect rolls back only that provider. Copilot reaching `default` closes the migration even if Gemini remains earlier on its independent ladder.
- After this map closes, the next implementation session activates `exec-plans`, mandatory `tdd`, and `official-sources`; rechecks the OKF v0.2 baseline; creates `docs/okf-kb-migration/implementation-execplan.md`; assigns explicit gate ownership; and begins only gate 1. The ExecPlan embeds the ten gates, path ledger, validation commands, evidence requirements, rollback checkpoints, and Gemini continuation contract without reopening these design decisions.

## Final confirmation

The user confirmed the complete three-round contract without further changes.

## Resolution

Deliver the migration through ten dependency-ordered acceptance gates. Gates 1 through 7 establish canonical Source Summary readiness; the profile, producer, and deterministic projection; the frozen evaluation v2 corpus, oracles, and legacy baseline; the shared selector, runtime, protocol, and fallback; both provider adapters and deterministic harnesses without production cutover; exact-build live-host qualification with both providers enrolled in `legacy`; and one atomic cross-provider cutover that retires the dedicated source-ingest hooks only after replacement parity and safe legacy behavior pass. Gates 8 through 10 are separate configuration-only commits promoting Copilot through `shadow`, `canary`, and `default`. Copilot reaching `default` completes the migration. Gemini remains fully implemented, qualified, and independently promotable through its own non-blocking ladder; the final handoff records its exact continuation state.

Give each gate one owner with exclusive control of implementation, tests, generated artifacts, and accompanying documentation, plus an independent acceptance reviewer. Transfer shared path ownership only between sequential gates. Gate 7 has one cross-provider owner and may not partially retire one provider's compatibility hooks. Land every accepted build or cutover gate as one atomic commit, commit qualification evidence separately from the adapter implementation it qualifies, and keep promotion commits configuration-only. Revert defective build or cutover commits as units; deployed rollback uses the accepted reviewed configuration change directly to `legacy`.

Use the accepted path ledger. Gate 1 owns the nine canonical summaries, `.agents/memory/INDEX.md`, and source-ingest manifest. Gate 2 owns `.agents/okf-profile.json`, projection code and tests, `scripts/okf-projection.py`, and generated `.agents/okf/`. Gate 3 owns evaluation v2 documentation, corpus, oracles, fixtures, baseline, and modules. Gate 4 owns shared selector, runtime, protocol, fallback, and tests under `scripts/agent_kb/` and `scripts/tests/agent_kb/`. Gate 5 owns `.github/extensions/agent-kb/extension.mjs`, the Gemini adapter under `.gemini/hooks/scripts/`, provider harnesses, and tests. Gate 6 owns `scripts/agent-kb-evaluate.py`, promotion CI, `.agents/okf-qualification/`, and `.agents/okf-runtime.json`. Gate 7 owns both providers' source-ingest registrations and retired scripts, replacement legacy tests, and any required runtime configuration. Gates 8 through 10 write only `.agents/okf-runtime.json`.

Store each exact deployment tuple's compact evidence at `.agents/okf-qualification/<provider>/<tuple-digest>.json`, including bound `shared_core` and provider verdicts, identities, thresholds, counts, and immutable artifact references. Bind the selected manifest from `.agents/okf-runtime.json` by repository-relative path and SHA-256 digest; do not create mutable `current` evidence. A `fail` or `incomplete` verdict stops qualification or promotion.

Treat these commands as stable public acceptance interfaces:

```text
python3 scripts/okf-projection.py generate
python3 scripts/okf-projection.py check
python3 -m unittest discover -s scripts/tests/agent_kb -p 'test_*.py'
python3 scripts/agent-kb-evaluate.py --partition promotion --provider all --format json
```

Use the evaluator's deployment-tuple input for live-host qualification and emit independent `shared_core`, `copilot`, and `gemini` verdicts. Run applicable existing hook, startup, observability, installer, shell-syntax, Python-compilation, and `git diff --check` checks cumulatively. Add neither a general build command nor a dependency.

Apply the detailed cumulative acceptance conditions from accepted round 3. Legacy remains authoritative through the core build gates. Do not weaken frozen oracles to admit an implementation. Keep existing source-ingest hooks active through adapter development and qualification; remove both providers' dedicated registrations and scripts together only after exact-build qualification, source-ingest parity, shared-runtime parity, qualified `legacy` behavior, installer validation, and proof of exactly one replacement context path. Every Copilot promotion preserves candidate and tuple bindings, passes exact-commit CI, completes the accepted observation window, and satisfies all zero-tolerance and frozen-envelope gates. Shared defects return every enrolled provider to `legacy`; provider defects roll back only that provider.

Documentation travels with gates 1 through 7: update affected instructions, memory maps, testing guidance, known issues, API documentation, and user-facing setup documentation in the same commit, then run `update-agent-docs` once at the end of the work session. Promotion evidence stays in CI artifacts and review records, so mode-only commits remain configuration-only.

The next session activates `exec-plans`, mandatory `tdd`, and `official-sources`; rechecks the OKF v0.2 baseline; writes `docs/okf-kb-migration/implementation-execplan.md`; assigns explicit ownership for the current gate; and begins gate 1 only. The ExecPlan carries this ticket's ten gates, paths, commands, acceptance evidence, commit and rollback boundaries, and Gemini continuation contract without reopening design decisions.
