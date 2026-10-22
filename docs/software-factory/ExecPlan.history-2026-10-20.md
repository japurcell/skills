# Historical research plan

Snapshot preserved on 2026-10-20. Background only: its durable-graph recommendation and review-next instructions are superseded by the accepted specification and active ExecPlan. This snapshot authorizes no work.

# Research and compare software factory designs

This living plan is `docs/software-factory/ExecPlan.md`. It follows `.agents/skills/exec-plans/SKILL.md`.

## Purpose / Big Picture

Study the examples in `docs/ideas.md`, then deliver three distinct interactive HTML architecture documents. A reader can inspect deterministic controls versus agent reasoning, walk through success and failure cases, compare tradeoffs, and save or export comments. These are research prototypes, not an operational factory. All example runs, usage figures, and agent responses must be labeled simulated.

The user's requirements are skill-based installation in arbitrary repositories, multiple customizable workflows, learning from previous runs, multiple models and coding harnesses, and one inspectable UI for live and historical runs. Deterministic control belongs in code; reasoning belongs in agents. The sources are kunchenguid/no-mistakes, disler/super-simple-software-factory, poteto/noodle, and the linked Shopify video. Unavailable evidence must remain explicitly unverified.

## Progress

- [x] (2026-10-08) [milestone-1] R1, R2, R3: inspect each repository and save cited findings.
- [x] (2026-10-08) [milestone-1] R4: investigate the video and synthesize evidence, gaps, and requirements.
- [x] (2026-10-12) [milestone-2] D1: create three distinct architecture prototypes and comparison entry point.
- [x] (2026-10-12) [milestone-2] D2: verify scenarios, annotations, export, accessibility, and layout in a browser.
- [x] (2026-10-12) [milestone-3] K1: complete the coordinated knowledge maintenance pass and delivery audit.

## Surprises & Discoveries

- RTK is installed at version 0.51.0, but `rtk gain` cannot open its tracking database. RTK-wrapped reads and Git commands work.
- No existing research subtree is present. Repository guidance places active research under `docs/<effort>/`.
- The video is AI LABS' reconstruction of Shopify Helix. Its English auto-generated transcript was retrieved through the browser export after web retrieval failed. The reconstruction changes reviewer roles and human approval timing.
- Bundled Playwright has no installed browser executable. The Codex in-app browser is available and will own UI verification.

## Decision Log

- 2026-10-08: Keep requested research and prototypes in `docs/software-factory/` while the architecture decision remains open. Treat them as user deliverables, not transient notes to delete.
- 2026-10-08: Use plain standalone HTML documents with inline CSS and JavaScript, so opening a file needs no build or service. Persist only user feedback in browser storage, with explicit export/import. Factory scenarios remain in memory.
- 2026-10-08: Build three architecture alternatives, not visual skins: a repo-local runner, a durable workflow graph, and an event-driven factory. Final mechanics depend on source findings.
- 2026-10-08: Do not add a test suite for disposable prototype documents. Verify behavior directly through the visible browser interface and inspect scripts for syntax. This follows the prototype skill and the higher-priority rule against tests for low-impact reversible changes.

## Outcomes & Retrospective

Research and three interactive design documents are complete, with cited source reports and explicit snapshot limitations. The comparison is open for user review. No architecture has been selected or validated for production. The initial recommendation is the durable graph, subject to annotations and implementation experiments. Review instructions and actual validation evidence are recorded in README.md and delegation.md.

## Context and Orientation

This repository publishes skills, agent instructions, and provider hooks. The current task changes only idea/research documents and prototype HTML. It does not change installed skills, hooks, or agent harnesses. Repository-wide entry guidance is in `AGENTS.md` and `.agents/instructions/INDEX.md`; applicable branches are repository workflow, testing, and end-of-session knowledge admission.

## Plan of Work

### Milestone 1: Evidence-backed source research
Status: done
Acceptance: met

R1 owns only `research/super-simple-software-factory.md`; R2 owns only `research/no-mistakes.md`; R3 owns only `research/noodle.md`, all under `docs/software-factory/`. Their prerequisites are the user's requirements and public repository access. Each investigates code, documentation, tests, and event/storage interfaces, records revision/date, cites primary files, distinguishes implemented behavior from intent, and stops after its report. All three may proceed in parallel. They must not execute upstream code or modify shared files.

R4 is coordinator-owned. It investigates the supplied video, verifies representative source claims, and writes `research.md` with the complete requirements, source comparison, synthesis, unknowns, and options. It depends on R1-R3 for repository conclusions. Source claims need traceable links; gaps must not become attributed facts.

Each research agent has a 12-minute runtime warning threshold, tracked by coordinator UTC timestamps and checked during normal progress checks. If overdue, send a non-interrupting warning requesting status, findings, blockers, and ETA. Submitted model and effort must match the printed route; runtime-executed settings remain unconfirmed unless the runtime reports them. Record final audits in `delegation.md`.

### Milestone 2: Reviewable interactive designs
Status: done
Acceptance: met

D1 depends on milestone 1. The coordinator creates `index.html`, `repo-runner.html`, `durable-graph.html`, and `event-factory.html` under `docs/software-factory/prototypes/`. Each design explains its question, topology, state ownership, workflow customization, harness/model routing, memory improvement, and operational tradeoffs. Native clickable diagrams expose components. Guided scenarios show success, failed checks, recovery, and bounded review loops. A timeline/detail inspector demonstrates live and past session views using simulated events. Feedback supports section or component anchors, selected text, editable comments, local persistence, and portable export/import.

D2 depends on D1 and owns browser verification. Open every file, exercise each scenario, inspect at desktop and narrow widths, verify comment persistence after reload, export/import feedback, keyboard navigation, and absence of clipped diagrams or text. Validate inline JavaScript syntax and local links. Report simulation limits and any unavailable browser capability.

### Milestone 3: Deliver evidence and clean documentation
Status: done
Acceptance: met

K1 depends on all research and prototype work completing. Activate `update-agent-docs`, review knowledge admission, repair the idea inbox pointer, inspect diffs, and record actual verification evidence. Do not create speculative memory. Open the comparison entry point in Codex and deliver links with short usage instructions and source limitations.

## Concrete Steps

Next action belongs to the user: inspect the alternatives and annotate design decisions. Research agents completed within the 12-minute warning threshold. Implementation of a real factory is outside this research task. All repository commands ran from `/Users/adam/.codex/worktrees/ea58/skills` through `rtk`.

## Validation and Acceptance

Source-linked reports cover all three repositories, the supplied video, Shopify's primary accounts, and documented harness interfaces. All twelve scenario paths were exercised in the browser. Component selection, historical events, configuration changes, quoted comments, persistence, editing, resolution, JSON export/import, invalid input, and keyboard dismissal were verified. Desktop and compact frame layouts were inspected without document overflow. A cross-view note overwrite was reproduced, fixed with per-note storage, and verified with two open design tabs after reload. Inline script syntax and embedded data checks pass; local links resolve. Detailed evidence and scope limits are in delegation.md.

## Idempotence and Recovery

Research reads are repeatable. Upstream clones or downloads belong in temporary directories and must not be run. Prototype simulations reset without touching repository content. Feedback export protects annotations when browser origin or file paths change. Import validates the document format and displays a clear failure for invalid input. No deployment, real agent execution, external messages, commits, or remote writes are part of this task.

## Interfaces and Dependencies

The prototypes use browser-native HTML, SVG, CSS, JavaScript, localStorage, and downloadable JSON. No third-party script or font is required. Event data is embedded. A portable feedback record contains version, design, anchor, selected quote, comment body, status, and timestamps. Source citations are ordinary HTTPS links. Browser verification may use the available computer-use tools or bundled browser runtime.

## Visual Document Direction

Use a workshop schematic as the central visual, with one continuous connector map and a quiet inspector. Base palette: paper `#f6f8fc`, ink `#182c45`, code blue `#2358a8`, reasoning violet `#7250a2`, human amber `#8b5915`, and evidence teal `#146b66`. System Avenir/Segoe UI carries prose; Georgia carries the short document title; monospace is reserved for code. Left-align content with a bounded reading width. Distinguish code, reasoning, evidence, and human decisions with explicit text as well as color.

Avoid a generic metrics dashboard: lead with the architecture and a question to test. Put controls beside their consequences, provide a clear scene description, and place comments in a persistent review drawer. The comparison page should expose operational tradeoffs, not invented numerical scores. All three design pages share annotation mechanics but use different topology and recovery scenarios.
