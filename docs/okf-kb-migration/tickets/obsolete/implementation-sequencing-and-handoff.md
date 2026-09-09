# Implementation Sequencing and Handoff

**Type:** grilling
**Status:** obsolete
**Blocked By:** none
**Research Dir:** N/A

## Question

How should the approved design be sliced into dependency-ordered vertical milestones with explicit file ownership, test and build commands, documentation obligations, commit boundaries, acceptance criteria, and rollback checkpoints so a later ExecPlan can be written without reopening design decisions?

---

<!-- Resolution will be appended here -->

## Resolution

Implement the migration as nine dependency-ordered vertical gates. Each gate has one owner for its complete path group, including implementation, tests, generated evidence, and documentation; an independent reviewer accepts the gate. Paths may transfer between sequential gates but never have concurrent writers. Land each accepted gate as one atomic, reviewable commit and keep the repository safe and usable at every boundary.

### Gate 1: Canonical Source Summary readiness

Repair the nine canonical Source Summaries, replace unsupported completed-summary verification metadata with selection-oriented `coverage`, remove completed-document stale-reason text, synchronize `.agents/memory/INDEX.md`, and update `.agents/memory/sources/source-ingest-manifest.json` through the existing reconciliation contract. The gate owner has exclusive write ownership of those summaries, index entries, and manifest. `.agents/sources/` remains immutable.

Acceptance requires all nine summaries to parse, all nine manifest entries to be `active` with matching live hashes, unchanged raw-source hashes, and passing Copilot/Gemini source-ingest parity tests. Legacy loading remains authoritative. A failed pre-merge gate is rejected; a merged defect is rolled back by reverting this atomic commit.

### Gate 2: Profile, producer, and deterministic projection

Add `.agents/okf-profile.json`, the public `scripts/okf-projection.py` entry point, its importable implementation under `scripts/agent_kb/`, tests under `scripts/tests/agent_kb/`, and the committed generator-owned `.agents/okf/` tree with `.projection-manifest.json`. This gate's owner exclusively controls the profile, producer implementation, producer tests, and every generated output.

Acceptance requires strict profile/source/OKF/graph/index/integrity validation; generate-twice byte identity; a clean read-only projection check; complete 42-concept output; deterministic negative diagnostics; no partial publication on validation failure; and no installer, hook, or runtime write to `.agents/okf/`. Revert the complete gate commit if a merged defect is found.

### Gate 3: Frozen evaluation contract and legacy baseline

Add the versioned, human-reviewed corpus and contract documentation under `docs/okf-kb-migration/evaluation/`, evaluation modules and fixtures under `scripts/agent_kb/` and `scripts/tests/agent_kb/`, deterministic mutations, provider replay vectors, and the same-revision legacy baseline. The evaluation owner controls these paths during the gate and hands their stable interfaces to later owners only after acceptance.

Acceptance requires valid development and frozen promotion partitions, every coverage obligation from `agent-kb-evaluation@1.0.0`, bound case and expected-output digests, reproducible legacy identities and byte totals, and exact expected outcomes for every single-fault mutation. The oracle is reviewed before selector optimization and is never weakened to admit an implementation. Roll back the gate commit if its contract or evidence is invalid.

### Gate 4: Shared selector and fallback runtime

Implement the provider-neutral selector, mandatory-context policy, lifecycle handling, budgets, dispositions, normalized runtime configuration parsing, and deterministic shared legacy loader under `scripts/agent_kb/`, with corresponding tests under `scripts/tests/agent_kb/`. The runtime owner exclusively controls these modules and tests during the gate.

Acceptance requires the complete selector ranking and audit contract, mandatory closure and ordering, atomic `use_okf`/`use_legacy`/`hard_stop` behavior, no mixed or partial context, stable reason codes, deterministic perturbation replay, offline and standard-library-only operation, no runtime writes, and every applicable corpus and mutation assertion. Revert the gate commit if a merged defect violates the contract.

### Gate 5: Provider integration without promotion

Add thin repository-owned Gemini and Copilot adapter integration at the existing `.gemini/settings.json`, `.gemini/hooks/scripts/`, `.github/hooks/hooks.json`, and `.github/hooks/scripts/` surfaces, plus their targeted test scripts. The integration owner controls both provider-local path groups together so behaviorally duplicated logic and parity fixtures remain synchronized.

Acceptance requires byte-identical provider-neutral results for identical normalized requests, provider-valid JSON-only envelopes, Gemini `BeforeAgent` hard-stop enforcement and `AfterAgent` final gating, current source-ingest reconciliation before selection, atomic legacy fallback, and an expected failing Copilot promotion-capability result until true pre-turn denial and prompt identity exist. Both providers remain configured for legacy behavior. Revert the gate commit for an integration defect.

### Gate 6: Promotion qualification and legacy-mode enrollment

Add the public `scripts/agent-kb-evaluate.py` runner, the promotion CI workflow, machine-readable exact-commit report generation, and `.agents/okf-runtime.json` with both providers in `legacy`. Evaluate the bounded budget candidates and commit the smallest byte-budget/concept-count pair that passes every gate, breaking ties by byte budget and then concept count. The promotion owner controls the runner, CI surface, evaluation updates, and runtime configuration during this gate.

Acceptance requires one complete exact-candidate report satisfying every semantic, mutation, determinism, provider-parity, recall, irrelevant-byte, latency, schema, and digest gate; passing installer and cross-platform validation; and no enabled OKF injection. Missing or inconsistent evidence fails closed. Revert the entire gate commit if its qualification or configuration is defective.

### Gates 7–9: Gemini rollout

Gate 7 changes only `.agents/okf-runtime.json` to put Gemini in `shadow`; shadow always serves legacy context while comparing OKF read-only. After a complete normal work cycle and at least 50 eligible prompts, freeze Gemini's operational envelope from privacy-safe shadow evidence. Gate 8 is a separate configuration-only commit advancing Gemini to an explicit canary branch or worktree. After its own restarted observation window passes, gate 9 is a separate configuration-only commit advancing Gemini to `default`.

Before every forward transition, require the complete exact-commit CI report and the applicable observation evidence. Candidate or runtime-configuration changes restart the evidence window. The release owner writes only `.agents/okf-runtime.json`; prompt-level evidence remains in protected provider observability storage, aggregate reports in CI artifacts, and promotion metadata in review records. Runtime code never changes rollout state.

Reject an unqualified transition before merge. After any deployed safety, integrity, parity, determinism, privacy, or disposition violation, immediately make a reviewed configuration change returning Gemini to `legacy`, not merely its previous rollout mode. Operational degradation first freezes promotion and triggers rollback only under the accepted provider-specific rolling-window envelope. Copilot remains `legacy` throughout these gates.

### Stable validation interface

The implementation ExecPlan treats these new commands as stable public acceptance interfaces:

```text
python3 scripts/okf-projection.py generate
python3 scripts/okf-projection.py check
python3 -m unittest discover -s scripts/tests/agent_kb -p 'test_*.py'
python3 scripts/agent-kb-evaluate.py --partition promotion --format json
```

Every gate also runs applicable existing targeted checks:

```text
python scripts/test_helpers.py
bash scripts/test-hooks-auto-ingest.sh
bash scripts/test-gemini-hooks-auto-ingest.sh
bash scripts/test-hooks-startup.sh
bash scripts/test-gemini-hooks-startup.sh
bash scripts/test-install.sh
pwsh -NoProfile -File scripts/test-install.ps1
bash scripts/test-hooks-observability.sh
bash scripts/test-gemini-hooks-observability.sh
bash -n scripts/install.sh
python3 -m py_compile <changed Python entrypoints>
git diff --check
```

Run targeted tests at every gate, cumulative agent-KB tests from gate 2 onward, provider parity suites from gate 5 onward, installer and cross-platform checks before shadow, and the complete promotion suite before every forward mode transition. This repository has no general build command; introducing one or adding a dependency requires a separate decision and approval.

### Documentation, commits, and implementation handoff

Documentation travels with gates 1–6 rather than waiting for a cleanup milestone. Each owner updates affected `.agents/instructions/`, testing and known-issue memory, file/API maps, and user-facing documentation in the same commit, then runs the mandatory `update-agent-docs` pass once at the end of the work session. Gates 7–9 remain configuration-only commits; their evidence lives in CI artifacts and promotion-review metadata, so no documentation catch-up is invented.

The next session activates `exec-plans`, mandatory `tdd`, and `official-sources`; rechecks the OKF v0.2 baseline; creates `docs/okf-kb-migration/implementation-execplan.md`; assigns explicit ownership for the current gate; and begins gate 1 only. The implementation ExecPlan spans completion of Gemini's rollout through `default`. This ticket is the canonical sequencing decision, and `docs/okf-kb-migration/handoff.md` remains the sole resume handoff; do not create a duplicate sequencing document.
