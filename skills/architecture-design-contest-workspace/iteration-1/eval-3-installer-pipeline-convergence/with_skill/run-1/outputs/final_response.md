# Problem framing

**Goal**
Converge `copilot-install.sh` and `scripts/copilot-install.sh` into one maintainable installation pipeline that preserves current behavior, reduces duplication risk, and makes future sync changes safer.

**Non-goals**
- Changing install semantics today
- Merging the local Copilot installer into `scripts/addy-install.sh`
- Writing code in this pass

**Hard constraints**
- The documented canonical entrypoint today is `./scripts/copilot-install.sh` (`README.md`, `AGENTS.md`, `docs/agent-guides/repo-layout.md`).
- `/home/adam/dev/personal/skills/copilot-install.sh` does **not** exist today, but git history shows it used to live at the repo root and was renamed into `scripts/` in commit `324d435`.
- Current behavior must stay intact: overlay copy into `~/.agents` / `~/.copilot`, skip `skills/*-workspace`, copy optional top-level `references/` and `hooks/` only when present, and require `.copilot/copilot-instructions.md`.
- Repo conventions favor directly executable Bash helpers and simple standard-library implementations.

**Unknowns**
- Whether you want a root-level compatibility alias restored for humans/old automation, or only implementation convergence.
- Whether “future sync changes” means just new asset types, or eventually stronger behaviors like verification/pruning/transforms.

**Decision criteria**
I compared directions by: simplicity, extensibility, migration cost, ease of correct use, operational/test complexity, and fit with current repo patterns.

# Codebase / research findings

- `scripts/copilot-install.sh` is a small local publisher: it validates required inputs, copies `skills/`, `agents/`, optional `references/`, optional `hooks/`, and `.copilot/copilot-instructions.md`, and skips `*-workspace` directories.
- The current installer is an **overlay copier**, not a full reconciliation engine: it does not prune stale installed content.
- `scripts/addy-install.sh` is the nearest neighboring pipeline, but it solves a different problem: upstream clone/pull, selective install, transitive dependency resolution, name rewriting, reference rewriting, pruning, and state-file updates.
- `scripts/test-addy-install.sh` is a useful precedent: the repo already accepts a shell-script behavioral test harness for installer logic, but `scripts/copilot-install.sh` currently only gets `bash -n` coverage in docs.
- Docs consistently teach `./scripts/copilot-install.sh` as the canonical path, which means any root-level `copilot-install.sh` should be a compatibility layer, not the new canonical implementation.
- Git history matters here: the root script already existed once, so bringing it back as a wrapper is a compatibility choice, not a novel interface.

# Design A — Compatibility shim over one canonical script

**What it optimizes for**
The smallest safe change: one real implementation, two valid invocation paths.

**Architecture overview**
Reintroduce `./copilot-install.sh` at the repo root as a tiny wrapper that immediately delegates to `./scripts/copilot-install.sh`. All real install logic continues to live only in `scripts/copilot-install.sh`.

**Component boundaries**
- `copilot-install.sh`: compatibility entrypoint only
- `scripts/copilot-install.sh`: sole implementation
- optional `scripts/test-copilot-install.sh`: proves wrapper and canonical path behave identically

**Data flow / integration points**
User runs either entrypoint -> root wrapper `exec`s `scripts/copilot-install.sh` -> existing installer performs the current overlay copy flow.

**Where it fits best**
When the main problem is path convergence and accidental duplication, not deeper installer evolution.

**Where it creates friction**
It does almost nothing for internal maintainability beyond preventing a second implementation from reappearing.

**Irreversible commitments**
You are explicitly supporting two human-facing entrypoints, even if only one is canonical in docs.

**Key risks / failure modes**
- Wrapper drift if logic ever leaks back into the root script
- Minor doc/user confusion if both paths look equally “official”
- Does not address future complexity inside the canonical installer itself

**Testing / migration implications**
Low-risk rollout. Add syntax checks for both files and preferably a black-box wrapper-equivalence test.

**Why it is materially different**
This is a UX and compatibility convergence strategy, not an internal pipeline redesign.

# Design B — Phase-oriented Bash pipeline under `scripts/lib/`

**What it optimizes for**
Safer future changes without abandoning the repo’s Bash-first style.

**Architecture overview**
Keep `./scripts/copilot-install.sh` as the canonical entrypoint, but refactor the implementation into explicit phases:
1. discover
2. plan
3. sync
4. verify
5. report

A root-level `copilot-install.sh` can optionally exist as a thin shim on top, but the main value is moving from a monolithic copier to a structured pipeline.

**Component boundaries**
- `scripts/copilot-install.sh`: thin orchestrator
- `scripts/lib/copilot-install/context.sh`: resolve repo root, sources, destinations, optional capabilities
- `scripts/lib/copilot-install/plan.sh`: compute copy operations and filters
- `scripts/lib/copilot-install/sync.sh`: execute current overlay semantics
- `scripts/lib/copilot-install/verify.sh`: postconditions and clearer failures
- `scripts/lib/copilot-install/report.sh`: consistent output

**Data flow / integration points**
Filesystem + env -> discover context -> build ordered install plan -> execute copy operations -> verify required outcomes -> print summary. This mirrors the stronger structure already visible in `scripts/addy-install.sh`, without importing addy-specific behaviors.

**Where it fits best**
When you expect the local installer to gain more policy over time: more asset types, safer verification, optional transforms, or shared utilities with future tooling.

**Where it creates friction**
More moving parts than today, and a new internal module layout to maintain.

**Irreversible commitments**
You are standardizing on a staged pipeline shape for future installer work.

**Key risks / failure modes**
- Over-structuring a small script
- Accidentally changing current overlay semantics while extracting phases
- New internal boundaries could feel heavy if the installer stays tiny forever

**Testing / migration implications**
This direction pairs naturally with a new `scripts/test-copilot-install.sh` modeled after `scripts/test-addy-install.sh`, because each phase becomes easier to exercise and reason about.

**Why it is materially different**
This is an internal architecture redesign around lifecycle stages, not just path convergence.

# Design C — Declarative manifest-driven install engine

**What it optimizes for**
Maximum future safety for adding or changing install surfaces.

**Architecture overview**
Move the install graph into a declarative manifest (for example: source, destination, required/optional, exclude pattern, copy mode), and make `scripts/copilot-install.sh` a thin engine that interprets that manifest.

**Component boundaries**
- `scripts/copilot-install.sh`: entrypoint / engine launcher
- `scripts/install.manifest` (or similar): canonical install graph
- `scripts/lib/install-engine.sh`: generic parser, validator, executor, reporter
- optional `copilot-install.sh`: compatibility shim to the canonical entrypoint

**Data flow / integration points**
Manifest declares operations -> engine validates required sources -> engine executes the copy plan -> engine reports results. Future changes like adding another installable top-level directory become manifest edits instead of shell-logic edits.

**Where it fits best**
When you expect frequent installer evolution and want the install contract to be inspectable as data rather than embedded in bash flow.

**Where it creates friction**
This is the highest-abstraction option. Debugging moves from “read the shell script” to “understand manifest + engine.”

**Irreversible commitments**
You are committing to a data-model for installation behavior and a small framework around it.

**Key risks / failure modes**
- Over-engineering relative to current scale
- Parser/quoting mistakes if the manifest format is too clever
- Harder contributor ramp-up versus a plain shell script

**Testing / migration implications**
It benefits the most from behavioral tests, because the manifest/engine seam becomes the contract. It also makes future agent edits safer: changing destinations or exclusions can often happen without touching executor logic.

**Why it is materially different**
This shifts the primary source of truth from imperative code to declarative installation metadata.

# Comparison

**Simplicity and cognitive load**
Design A is by far the simplest. Design B is still readable for a Bash-centric repo, but introduces internal modules. Design C has the highest abstraction cost.

**Extensibility without over-generalizing**
Design B is the best middle ground. It gives you room for more checks and policy without inventing a framework. Design C is the most extensible, but also the easiest to overbuild.

**Implementation efficiency and migration cost**
Design A is cheapest. Design B is moderate and mostly mechanical. Design C is the heaviest because you must design both a manifest shape and an engine.

**Ease of correct use vs ease of misuse**
Design A reduces path misuse but does not make internal changes safer. Design B improves internal correctness by separating planning, copying, and verification. Design C is safest for future structural edits once established, but easiest to misuse during initial design if the schema is under-specified.

**Operational and testing complexity**
Design A has the lightest operational cost. Design B gives you the clearest path to add `scripts/test-copilot-install.sh` without much conceptual overhead. Design C benefits most from tests, but also requires them the most.

**Alignment with existing repo patterns**
Design A and B align best with the repo’s current Bash-helper conventions. Design C is still plausible, but it is the furthest from today’s “simple executable shell script” norm.

**Where the designs diverge most**
- Design A changes the surface area, not the internal architecture.
- Design B changes the internal architecture, but stays imperative and Bash-native.
- Design C changes the source of truth itself, making installation behavior data-driven.

# Recommendation

**Recommended direction: a hybrid of Design B + Design A.**

Use **Design B** as the real maintainability move:
- keep `./scripts/copilot-install.sh` canonical
- refactor it into discover/plan/sync/verify/report phases under `scripts/lib/`
- add a behavioral `scripts/test-copilot-install.sh` modeled after `scripts/test-addy-install.sh`

Add **Design A** only if you want explicit path convergence for humans and old automation:
- restore `./copilot-install.sh` as a tiny compatibility shim
- keep docs still pointing at `./scripts/copilot-install.sh`

I would **not** start with Design C unless you already expect frequent additions to the install surface (more asset classes, conditional destinations, transforms, or policy variants). It is powerful, but probably one step more abstract than this repo needs right now.

**Why this recommendation wins**
It preserves current behavior, keeps the documented path stable, materially improves change safety through phase separation and tests, and avoids introducing a framework before the repo has proved it needs one.

# Next design decision

The one question that most changes the shape is:
**Do you want the repo root `copilot-install.sh` restored as a supported compatibility alias, or do you only want one public path and one internal pipeline?**

If you want, I’d choose one of these next:
1. **Recommended hybrid (B + optional A)** — phase-oriented canonical pipeline, plus a root shim if compatibility matters.
2. **Design A only** — fastest convergence with minimal churn.
3. **Design C** — invest now in a declarative engine because you expect the installer surface to keep growing.
