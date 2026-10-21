---
name: code-modernization
description: Modernize legacy codebases with a guided, stepwise process that produces an executive brief
argument-hint: <subcommand> <system-dir> [target-stack]
disable-model-invocation: true
compatibility: Requires python3, scc or cloc, lizard, glow, and delta or diff
---

# Code Modernization

Point at a legacy codebase — COBOL, legacy Java/C++/.NET, monolith web apps — and get back: an executive assessment, an interactive architecture map, the business rules mined out of the code, a steering-committee-ready modernization brief, and scaffolded or transformed new code with a behavior-equivalence test harness so you can prove nothing drifted.

It works by enforcing a sequence, because modernization usually fails when teams skip steps — transforming code before understanding it, or shipping without a harness to catch behavior drift:

```
preflight → assess → map → extract-rules → brief → (reimagine | transform | uplift) → harden
```

The discovery commands (`assess`, `map`, `extract-rules`) write artifacts to `analysis/<system>/`. `brief` synthesizes them into an approval gate. The three build commands write to `modernized/<system>/` and are three different _methods_ — the brief recommends which one fits:

- **`transform`** — cross-stack rewrite from extracted intent (e.g. COBOL → Java).
- **`reimagine`** — greenfield rebuild on a new architecture.
- **`uplift`** — same-stack version bump (e.g. .NET Framework → .NET 8) that _preserves_ the code and fixes only the version deltas.

![Interactive topology map of AWS CardDemo — domains as containers, modules sized by lines of code, dependency edges colored by kind, entry points ringed](assets/topology-viewer-screenshot.jpg)

## Quickstart

Each command takes a `<system-dir>` and assumes the code lives at `legacy/<system-dir>/`. Artifacts land in `analysis/<system-dir>/`; new code in `modernized/<system-dir>/`. If your code is elsewhere, symlink it: `mkdir -p legacy && ln -s /path/to/code legacy/billing`.

Try the first three on your own codebase — each produces a standalone artifact, so you can stop and review at any point:

```bash
/code-modernization preflight billing      # is my environment ready?
/code-modernization assess billing         # what am I dealing with?
/code-modernization map billing            # show me the structure (opens an interactive map)
```

Then the full path:

```bash
/code-modernization extract-rules billing                              # mine business rules → testable Rule Cards
/code-modernization brief billing java-spring                          # the plan a steering committee approves (HITL gate)
/code-modernization transform billing interest-calc java-spring        # …or reimagine, or uplift — see Commands
/code-modernization harden billing                                     # security pass on the still-running legacy system
/code-modernization status billing                                     # where am I, what's stale, what's next
```

## Commands

Run in order, but each is standalone — stop, review, resume.

- **`/code-modernization preflight <system-dir> [target-stack]`** — [Environment readiness check](commands/modernize-preflight.md). Asks you the five questions the source can't answer (scope, whether you can build and test locally, bespoke build infrastructure, prior attempts, what's off limits), then detects the legacy stack, checks analysis tooling, reads the CI/build definition for how the system builds, smoke-tests the toolchain against the real code, inventories missing includes / deployment descriptors, and checks the **scope boundary** — whether `<system-dir>` is a slice of a larger repo and what outside it depends on it. Produces `PREFLIGHT.md` with a per-command Ready / Ready-with-gaps / Not-ready verdict.

- **`/code-modernization assess <system-dir>`** _(or `--portfolio <parent-dir>`)_ — [Inventory and COCOMO assessment](commands/modernize-assess.md). Inventory: languages, complexity, tech debt, security posture, and a COCOMO complexity index ([see note](#a-note-on-cocomo)). Produces `ASSESSMENT.md` + `ARCHITECTURE.mmd`. With `--portfolio`, sweeps every subdirectory and writes a sequencing heat-map (`portfolio.html`).

- **`/code-modernization map <system-dir>`** — [Interactive topology map](commands/modernize-map.md). Dependency and topology map: call graph, data lineage, entry points, and 2–4 business flows each traced for a persona (the claimant, the auditor). Produces `topology.json` and an **interactive zoomable `TOPOLOGY.html`** (circle-pack sized by LOC, edge toggles, search, and a persona-flow walkthrough), plus small `.mmd` diagrams for docs.

- **`/code-modernization extract-rules <system-dir> [module-pattern]`** — [Business rule mining](commands/modernize-extract-rules.md). Mine the business rules — calculations, validations, eligibility, state transitions — into Given/When/Then "Rule Cards" with `file:line` citations and confidence ratings. Produces `BUSINESS_RULES.md` + `DATA_OBJECTS.md`.

- **`/code-modernization brief <system-dir> [target-stack]`** — [Phased modernization brief](commands/modernize-brief.md). Synthesize discovery into a phased **Modernization Brief**: target architecture, phase plan, persona walkthroughs, behavior contract, and an approval block. Reads the discovery artifacts and **stops if any are missing**. Enters plan mode as a human-in-the-loop approval gate. For a same-stack uplift it also requires the **delta catalog**, since an uplift's phase order is decided by its version deltas. The execution commands read the brief and treat each phase's entry criteria as gates, so editing the brief steers execution.

- **`/code-modernization reimagine <system-dir> <target-vision>`** — [Greenfield reimplementation](commands/modernize-reimagine.md). Greenfield rebuild from extracted intent. Mines a spec, designs and adversarially reviews a target architecture, then scaffolds services with executable acceptance tests under `modernized/<system>-reimagined/`. Two human checkpoints.

- **`/code-modernization transform <system-dir> <module> <target-stack>`** — [Single-module transform](commands/modernize-transform.md). Surgical single-module rewrite (strangler-fig: replace one piece while the legacy system keeps running). Plans first (approval gate), writes characterization tests, then an idiomatic implementation, and proves equivalence by running the tests. Produces `TRANSFORMATION_NOTES.md`.

- **`/code-modernization uplift <system-dir> <source-version> <target-version> [project-pattern]`** — [Same-stack uplift migration](commands/modernize-uplift.md). Same-stack version bump (e.g. `.NET Framework 4.8` → `.NET 8`, Spring Boot 2 → 3) — the common case `transform` gets wrong by rewriting. Preserves the code and makes the smallest diffs that compile and behave identically, driven by a **delta catalog** (the known breaking changes that _this_ code actually hits) and the ecosystem's migration tooling. Equivalence is proven by running the test suite on both the old and new runtime where both can run here (otherwise it falls back to characterization tests, like `transform`). Migration is **pilot-first**: one representative project is migrated end-to-end in-session and its lessons written to a `PLAYBOOK.md` before anything else is touched; the rest then fan out, one agent per project, in **dependency-aware escalating batches behind a circuit breaker**. Produces `DELTA_CATALOG.md`, `BASELINE.md`, `PLAYBOOK.md` + `UPLIFT_NOTES.md`. If the catalog shows most of the code is forced to change, it tells you to use `transform` instead.

- **`/code-modernization harden <system-dir>`** — [Legacy system security hardening](commands/modernize-harden.md). Security pass on the **legacy** system: OWASP/CWE, dependency CVEs, secrets, injection. Produces `SECURITY_FINDINGS.md` (ranked) and a reviewed `security_remediation.patch`. **Never edits `legacy/`** — you review and apply the patch yourself. Useful while the legacy system keeps running in production during migration.

- **`/code-modernization status <system-dir>`** — [Modernization progress status](commands/modernize-status.md). Read-only progress report: artifact inventory, staleness flags, secrets-hygiene checks, and the single most useful next command.

## Agents

Specialist subagents invoked by the commands (or directly):

- **`legacy-analyst`** — Reads legacy code (COBOL, EJB, classic ASP, …) and produces structural summaries; spots implicit dependencies and "JOBOL" (procedural code in modern syntax). _(assess, reimagine, uplift)_
- **`business-rules-extractor`** — Mines domain rules from procedural code with source citations. _(extract-rules, reimagine)_
- **`architecture-critic`** — Skeptical reviewer of target designs and transformed code; flags over-engineering. _(reimagine, transform, uplift)_
- **`security-auditor`** — Auth, input validation, secrets, dependency CVEs. _(assess, harden)_
- **`test-engineer`** — Characterization and equivalence tests that pin legacy behavior. _(transform, uplift)_
- **`version-delta-analyst`** — Finds the breaking changes between two versions of one stack that bite _this_ codebase, and drives the ecosystem migration tool. _(uplift)_
- **`uplift-migrator`** — Migrates one project/module of an in-flight uplift by following the pilot's playbook, then runs that unit's real build to prove it; refuses to migrate anything if no playbook exists yet. Writes only inside its own unit's directory. _(uplift)_
- **`scaffolder`** — Builds one service of a reimagined system; writes only within its own `modernized/.../<service>/` directory. _(reimagine)_

## Recommended workspace setup

A `.gemini/settings.json` or `.copilot/settings.json` in the project you're modernizing enforces the core invariant — never touch `legacy/`, freely edit `analysis/` and `modernized/`:

```json
{
  "permissions": {
    "allow": [
      "Read(**)",
      "Write(analysis/**)",
      "Write(modernized/**)",
      "Edit(analysis/**)",
      "Edit(modernized/**)"
    ],
    "deny": ["Edit(legacy/**)", "Write(legacy/**)"]
  }
}
```

This guards the file tools; shell commands that mutate files (`sed -i`, `git apply`) still go through the normal Bash prompt, so review those with the same invariant in mind. That prompt is the containment for the two steps that fan out many write-capable agents at once — `/code-modernization uplift` Step 5b and `/code-modernization reimagine` Phase E — so keep Bash on a _prompted_ permission mode for those.

## Prerequisites

Commands degrade gracefully, but these improve the output (run `/code-modernization preflight` to check all at once):

- **Analysis tools** — [`scc`](https://github.com/boyter/scc) or [`cloc`](https://github.com/AlDanial/cloc); without them, metrics fall back to `find`/`wc`.
- **A build toolchain** for the legacy stack — enables the strongest equivalence proof (live dual execution). Not required: without it, equivalence falls back to recorded-trace tests and preflight reports Ready-with-gaps rather than blocking.
- **The whole system in the tree** — deployment descriptors (JCL, CICS, route configs), copybooks/includes, DDL. Entry-point detection and data lineage need them.

## Safety notes

**Analyzed code is untrusted input.** A hostile codebase can plant comments like "ignore previous instructions" or "mark this rule approved" to steer what lands in `BUSINESS_RULES.md` or `SECURITY_FINDINGS.md`, which later commands trust. Defenses: agents treat file content as data and flag instruction-shaped text; verification agents re-derive every rule and finding from the cited code, not from another agent's description; filesystem paths are validated; and `/code-modernization brief` is a human approval gate before any code is generated. Treat discovery artifacts from untrusted code with the same skepticism as the code itself.

**Secrets stay out of shared artifacts.** Discovered credentials are masked (`AKIA****`) and inventoried in a gitignored `SECRETS.local.md` (or `~/.modernize/<system>/` on non-git projects); `/code-modernization harden` keeps credential-removal hunks in a separate gitignored patch. Pass `--show-secrets` to include raw values in the quarantine file only. If you ran an early version of this plugin on a real system, check whether `analysis/` artifacts were committed and rotate anything exposed.

### A note on COCOMO

`assess` derives a COCOMO figure from code size and uses it **only as a relative complexity/scale index** to rank and sequence systems — never as a timeline or cost. COCOMO's constants encode human-team productivity, which agentic transformation doesn't follow, so any duration derived from it would be wrong.

## Dynamic workflow orchestration

On agent runtimes supporting Workflow orchestration, five commands (`extract-rules`, `harden`, `assess --portfolio`, `reimagine`, `uplift`) run as scripted multi-agent orchestrations that fan out more agents for deeper coverage — looping until findings stabilize, and adversarially verifying each finding before it's written. `uplift`'s migration fan-out runs in dependency-aware escalating batches behind a per-batch **circuit breaker**, so a playbook that stops working is caught within a handful of agents and the spend stops until it is revised. They fall back to direct subagent fan-out on other agent platforms automatically; no configuration needed. Invoking the command is the opt-in.
