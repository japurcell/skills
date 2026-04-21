# Problem framing

**Goal**: add a new `/benchmark-triage` skill that reads a skill benchmark iteration directory (or its `benchmark.json`) and tells the user what to change next.

**Non-goals**: implementing the skill now, changing benchmark schemas, or replacing `skill-creator`’s analyzer/viewer pipeline.

**Hard constraints**:
- fit repo patterns from `skill-creator`, `create-plan`, and `implement-plan`
- accept the messy reality of benchmark workspaces and iteration layouts
- preserve the self-contained, forked, per-eval deep-dive workflow already captured for `benchmark-triage`
- balance reusability against keeping the workflow lightweight

**Assumptions**:
- v1 should accept either an iteration directory or `benchmark.json`
- the output is a short actionable triage report, not an auto-editing tool
- first release only needs to reason about one iteration at a time

**Decision criteria**: simplicity, reusability, correctness under partial artifacts, alignment with existing skill patterns, and ease of evolving later.

# Codebase / research findings

A few repo facts shape the design:

- `create-plan` and `implement-plan` are **staged, artifact-driven, and contract-heavy**. They use named gates, predictable sections, and explicit readiness handoffs rather than freeform responses.
- `skill-creator`’s benchmark flow is already a pipeline: run evals → grade → aggregate → analyze → review. A new triage skill should sit **after** that, not reinvent it.
- Benchmark inputs are **heterogeneous**. `aggregate_benchmark.py` and `generate_review.py` both tolerate multiple iteration layouts and discover runs from structure instead of hardcoded paths.
- The existing `analyzer` role is **observational only**. `benchmark-triage` needs to be the actionable layer that turns patterns into next edits.
- The confirmed `benchmark-triage` precedent already fixes some UX: `/benchmark-triage $benchmark_path`, self-contained execution, and selective per-eval deep dives.
- Timing and token metrics exist, but workspace examples show they are useful as secondary signals, not primary decision-makers.

That points to one big architectural tension: the repo rewards explicit stages and contracts, but benchmark artifacts are messy enough that a too-rigid implementation will be fragile.

# Design A — Lightweight SKILL-first triager

**Thesis**: keep almost all logic in `skills/benchmark-triage/SKILL.md`, reuse existing benchmark artifacts directly, and only fork task agents for a few representative failing evals.

**What it optimizes for**
- fastest path to a usable skill
- lowest maintenance burden
- behavior that feels close to the confirmed source session

**Architecture overview**
- `SKILL.md` is the main product.
- The skill resolves `$benchmark_path`, reads `benchmark.json` if present, then inspects nearby `eval-*`, `grading.json`, `timing.json`, `eval_metadata.json`, and `outputs/` as needed.
- It clusters failures in-model, flags likely flaky assertions, and launches targeted task-agent deep dives only for the worst regressions or highest-variance evals.
- It returns one strict report with sections like `Input status`, `Failure clusters`, `Representative deep dives`, `Recommended next edits`, and `Next command`.

**Component boundaries**
- `SKILL.md`: workflow, gates, and report contract
- optional tiny bundled reference: triage heuristics / report template
- task agents: per-eval deep dives only

**Where it fits best**
- v1 launch
- teams that want a lightweight skill before investing in reusable tooling
- cases where the benchmark artifacts are mostly complete already

**Where it creates friction**
- the clustering logic lives mostly in prompt instructions, so consistency may vary run to run
- if iteration layouts keep drifting, `SKILL.md` can become long and hard to maintain
- harder to reuse the triage logic elsewhere because the intelligence is mostly implicit

**Irreversible commitments**
- commits the skill to an instruction-led design rather than a helper-script-led one
- makes the report contract the main stable interface, not any intermediate artifact

# Design B — Normalized triage pipeline

**Thesis**: treat benchmark triage as a typed pipeline — validate → normalize → cluster → recommend — with a small helper script and explicit intermediate data contracts.

**What it optimizes for**
- reuse across messy benchmark layouts
- deterministic analysis
- future extension into a broader benchmark toolkit

**Architecture overview**
- `SKILL.md` orchestrates stages, but a bundled script normalizes raw benchmark artifacts into a canonical structure.
- The skill first validates the benchmark path, then converts runs into normalized per-expectation records.
- Cluster analysis runs on that canonical form, not on ad hoc file reads.
- Deep-dive agents only handle cases the normalized analysis marks as structural failures or flaky outliers.
- The final report is produced from structured data and could optionally emit machine-readable triage artifacts later.

**Component boundaries**
- `SKILL.md`: orchestration and output contract
- `scripts/normalize_benchmark.py`: tolerant benchmark ingestion / normalization
- `references/triage-taxonomy.md`: cluster definitions and thresholds
- `references/recommendation-templates.md`: mapping from failure type to proposed edit type
- task agents: targeted deep dives

**Where it fits best**
- if you expect multiple future skills or tools to consume triage results
- if benchmark layouts are inconsistent enough that inline reasoning becomes noisy
- if you want stronger repeatability across runs

**Where it creates friction**
- heavier than the workflow likely needs on day one
- adds maintenance surface next to `aggregate_benchmark.py` and `generate_review.py`
- risks feeling overbuilt compared with the lightweight style of many repo skills

**Irreversible commitments**
- introduces intermediate contracts that other tools may start depending on
- makes helper scripts part of the skill’s long-term maintenance story

# Design C — Hybrid staged triager

**Thesis**: keep the skill primarily instruction-led, but borrow `create-plan` / `implement-plan`’s explicit gates and handoff semantics so the workflow stays lightweight while still being reusable and disciplined.

**What it optimizes for**
- best balance of lightweight workflow and future reuse
- predictable user-facing output
- easier evolution if benchmark-triage proves valuable

**Architecture overview**
- `SKILL.md` stays the center of gravity.
- The workflow is explicitly staged:
  1. **Input Gate** — resolve iteration directory vs `benchmark.json`, verify enough evidence exists, and stop cleanly on incomplete inputs.
  2. **Benchmark Context Loaded** — read benchmark summary first, then selectively inspect nearby grading/output artifacts for the most informative evals.
  3. **Failure Cluster Analysis** — group repeated failures into a small fixed taxonomy (workflow gap, assertion problem, flaky/non-deterministic, marginal prompt fit).
  4. **Representative Deep Dives** — fork task agents only for a few high-leverage evals.
  5. **Recommended Next Edits** — produce a strict report with ranked edits and one next command.
- Instead of a full normalization subsystem, this version can optionally call existing `skill-creator` helpers when the workspace is incomplete or ambiguous, but it does not create a new general-purpose benchmark-processing layer.

**Component boundaries**
- `SKILL.md`: staged workflow, gates, and output contract
- one small reference file: failure taxonomy + edit categories
- optional tiny helper only for input resolution / fallback aggregation if benchmarking artifacts are incomplete
- task agents: representative per-eval deep dives

**Where it fits best**
- the repo as it exists today
- a first implementation that still wants clean structure
- users who care about maintainability but do not want a mini framework yet

**Where it creates friction**
- some clustering still happens in-model, so it is less deterministic than Design B
- slightly more ceremony than Design A
- may eventually need a fuller normalization script if benchmark consumers multiply

**Irreversible commitments**
- commits to named stages and a fixed report contract early
- keeps reusable logic relatively shallow until proven necessary

# Comparison

**Simplicity and cognitive load**
- **A** is the simplest. One main skill file, selective deep dives, minimal moving parts.
- **B** is the heaviest. It is clean architecturally, but it asks maintainers to own a second benchmark-processing layer.
- **C** is in the middle: more structure than A, much less machinery than B.

**Extensibility without over-generalizing**
- **A** is the least extensible. It works, but future reuse mostly means copying prompt logic.
- **B** is the most extensible. It is the strongest if benchmark triage becomes a broader platform concern.
- **C** is the best “extensible enough” option: stable stages and taxonomy now, script-heavy normalization later only if justified.

**Implementation efficiency and migration cost**
- **A** is cheapest to build and easiest to land.
- **B** has the highest upfront cost and the most testing surface.
- **C** is still efficient to implement, but it gives you a cleaner migration path if the skill later needs helper code.

**Ease of correct use vs ease of misuse**
- **A** is easy to invoke, but easier to drift because so much depends on prompt interpretation.
- **B** is hardest to misuse once built, because the contracts are explicit.
- **C** improves correctness materially over A by adding gates and explicit report sections without forcing B’s full machinery.

**Operational and testing complexity**
- **A** has the least operational complexity, but also the weakest deterministic testing story.
- **B** has the strongest testing story, but the most ops and maintenance overhead.
- **C** keeps testing practical: validate staged behavior and output sections first, then add a helper only if repeated failures demand it.

**Alignment with existing repo patterns**
- **A** aligns well with the repo’s general “skills are centered on `SKILL.md`” convention.
- **B** aligns well with the repo’s artifact-driven pipeline philosophy, but risks overshooting the lightweight feel of many existing skills.
- **C** aligns best overall because it combines the repo’s two strongest patterns: skill-centered authoring from `skill-creator`, plus gate/report discipline from `create-plan` and `implement-plan`.

# Recommendation

I’d build **Design C**.

It takes the part of **A** that matters most — keeping `/benchmark-triage` light, self-contained, and close to the confirmed workflow — and combines it with the part of **B** that matters most — explicit stages, a fixed taxonomy, and predictable outputs.

Concretely, I would start with:
- a `SKILL.md`-first implementation
- a fixed five-stage workflow
- a strict triage report contract
- a small shared taxonomy/reference file
- targeted task-agent deep dives
- optional fallback use of existing `skill-creator` helpers when the benchmark path is messy

I would **not** start with a full normalization subsystem unless one of these becomes true:
1. multiple skills need to consume triage artifacts,
2. benchmark layout drift starts causing recurring false diagnoses, or
3. you want machine-readable triage outputs to feed later automation.

So the recommendation is:
- **ship Design C first**
- **borrow Design B’s normalization ideas only as a future escalation path**
- **avoid Design A’s “all logic in one file forever” trap**

# Next design decision

The main thing still worth deciding before implementation is this:

**Should v1 be chat-only, or should it also save a `triage.md` artifact beside the benchmark iteration?**

That choice changes the design a bit:
- **chat-only** keeps the workflow lighter
- **saved artifact** makes future iteration tracking and handoff much easier

If you want, choose one of these paths and I’ll turn it into an implementation-ready spec next:
1. **Recommended** — Design C as-is
2. **Leanest possible** — Design A
3. **Most reusable** — Design B
4. **Hybrid tweak** — Design C, but with a saved `triage.md` artifact from day one
