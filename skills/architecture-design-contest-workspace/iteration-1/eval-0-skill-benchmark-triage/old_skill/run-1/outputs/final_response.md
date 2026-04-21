I’d lock three decisions up front before we compare shapes.

First, `/benchmark-triage` should be a forked, self-contained workflow rather than an interactive one; that matches the captured benchmark-triage session. Second, its input should be either an iteration directory or a `benchmark.json`, but it should be allowed to read nearby `grading.json`, `eval_metadata.json`, `analyzer-notes.json`, and representative outputs when it needs evidence. Third, its job should be prescriptive triage — “what do I change next?” — not just analyzer-style observations. That framing fits `skills/skill-creator/SKILL.md`, `agents/analyzer.md`, and the phase-and-gate/report-contract style used by `skills/create-plan/SKILL.md` and `skills/implement-plan/SKILL.md`.

### Option 1: Contract-first triage pipeline

This is the reusable architecture.

`/benchmark-triage` becomes a small orchestrator skill sitting on top of a normalized triage model. The skill resolves the input path, builds a single internal “triage context” from `benchmark.json`, analyzer notes, per-eval metadata, and grading artifacts, routes only the most important evals into deep dives, then renders a strict report. I would give it a `SKILL.md`, an input-contract reference, a triage-taxonomy reference, and a small set of helpers/scripts for normalization and report rendering.

The big advantage is reuse. `skill-creator` could call the same normalization rules after aggregation. Future tooling could reuse the same issue buckets: non-discriminating assertions, flaky evals, “skill hurts baseline”, “expensive without benefit”, “eval bug vs skill bug”. It also fits the repo’s strongest existing pattern: explicit phases, gates, and exact report sections rather than freeform advice. `create-plan` and `implement-plan` both work that way, and this option would too.

The cost is weight. You are introducing internal contracts, references, and helper boundaries before you know whether benchmark triage will stay narrow. It is the safest option for correctness and long-term reuse, but it is also the easiest one to overbuild.

### Option 2: Lightweight single-pass triage skill

This is the fast, specialized architecture.

Here `/benchmark-triage` is mostly one `SKILL.md` plus, at most, one small script that reads the iteration directory, clusters failures, flags flaky or non-discriminating assertions, and emits one markdown report. It would intentionally avoid reusable abstractions. No normalized intermediate model, no shared taxonomy files, no reusable worker contracts. Just intake, scan, optional spot-check of a few evals, then report.

This option fits the repo’s “small skill package” shape very well: `SKILL.md` as the entry point, maybe one helper script in `scripts/`, maybe one short reference pointing back to `skills/skill-creator/references/schemas.md`. It also matches the captured forked benchmark-triage workflow closely: read summary, inspect a few outliers, synthesize next edits, stop.

The downside is that the workflow logic and the analysis logic start to collapse into one place. That keeps it light, but it also makes it easier to drift. As soon as you want better evidence handling, clearer gates, or reuse inside `skill-creator`, you’ll be refactoring a narrowly written tool.

### Option 3: Thin orchestrator with optional deep-dive workers

This is the balanced architecture, and it’s the one I’d bet on.

The core idea is: keep the default path as light as Option 2, but make one architectural separation that matters. The top-level skill handles only five things: resolve input, run an intake gate, do one benchmark-wide scan, choose up to a few high-value deep dives, and emit a strict report. Everything else is optional. Deep dives are playbooks, not a full subsystem.

In practice, I’d structure it as `SKILL.md`, one small helper for reading benchmark artifacts, and one reference/playbook for per-eval deep dives. The report contract should be explicit and stable, borrowing the style of `create-plan` and `implement-plan`. Something like: `Triage target`, `Gate results`, `What the benchmark says`, `What to change next`, `Eval fixes before trusting the result`, `Next run`, `Open risks`.

This option composes cleanly with `skill-creator`. The insertion point is obvious: run evals, grade, aggregate benchmark, generate analyzer notes, then run triage before the next edit pass. It also preserves the forked benchmark-triage session’s most useful behavior: only spawn per-eval deep dives when the summary data says they are worth it.

### How they really differ

The biggest divergence is where you put structure.

Option 2 puts structure in the operator’s head and in one narrow workflow. That makes it the simplest thing to read and the fastest thing to land, but also the easiest to misuse once the workflow grows. Option 1 pushes structure into explicit contracts and reusable components. That makes it the hardest to misuse and the most general-purpose, but it asks you to pay the abstraction cost immediately.

Option 3 is the middle path. It keeps the default user experience lightweight, but it borrows the two patterns this repo already rewards: gate the workflow early, and make the final output contract exact. Compared with Option 2, it is more reusable without becoming a mini-framework. Compared with Option 1, it avoids inventing a whole internal platform before you know you need one.

In terms of implementation efficiency, Option 2 wins the first iteration and loses the second or third. Option 1 loses the first iteration and probably wins once multiple tools need the same benchmark-reading logic. Option 3 is the best compromise: fast enough to build soon, structured enough not to become throwaway. In terms of ease of correct use versus ease of misuse, Option 1 is strongest, Option 2 is weakest, and Option 3 is “safe by default” without much ceremony.

### Recommendation

I’d choose **Option 3: thin orchestrator with optional deep-dive workers**.

It fits the repo patterns best. `skill-creator` already owns execution, grading, aggregation, and iteration. `benchmark-triage` should not become another giant controller; it should be the decision layer that turns benchmark evidence into the next edit plan. The balanced version gives you that without forcing premature shared infrastructure.

If you want a concrete rule: choose Option 2 only if the goal is to prove the workflow in one quick pass and you’re comfortable rewriting it later. Choose Option 1 only if you already expect `skill-creator` or future tools to reuse triage internals directly. Otherwise, Option 3 is the right default.

Two external references reinforce that choice. JSON Schema’s emphasis on machine- and human-readable contracts is a good argument for making the report shape and any intermediate evidence shape explicit rather than implied (https://json-schema.org/overview/what-is-jsonschema). LangGraph’s workflow guidance also maps well here: do one orchestrated scan, then route only the highest-value cases into parallel workers instead of parallelizing everything by default (https://docs.langchain.com/oss/python/langgraph/workflows-agents).

If we move forward later, I’d turn Option 3 into a file-by-file implementation plan before writing the skill.