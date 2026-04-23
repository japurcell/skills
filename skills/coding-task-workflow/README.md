# coding-task-workflow

A portable, reusable skill that gives any AI agent a **deterministic end-to-end workflow** for coding tasks, plus a **repo bootstrap** phase that synthesises repo-local override files from existing documentation.

---

## Table of Contents

1. [What this skill is](#what-this-skill-is)
2. [Installation](#installation)
3. [How the workflow works](#how-the-workflow-works)
4. [How bootstrap works](#how-bootstrap-works)
5. [Repo-local files generated in target repos](#repo-local-files-generated-in-target-repos)
6. [GitHub issue and PR integration](#github-issue-and-pr-integration)
7. [Example usage scenarios](#example-usage-scenarios)
8. [Reference files](#reference-files)

---

## What this skill is

`coding-task-workflow` is a skill package for AI agents. When invoked, it instructs the agent to follow a structured, multi-phase process for any non-trivial coding task:

- **Isolation**: creates a git worktree so work never touches the main branch until it is ready.
- **Exploration**: uses parallel subagents to understand the codebase before any design decisions are made.
- **Research**: uses parallel subagents to answer open questions against up-to-date official documentation and best practices.
- **Minimal human interaction**: asks the human only for clarifications that cannot be resolved through exploration or research.
- **Explicit design gate**: a written plan is approved before implementation begins.
- **TDD-first implementation**: work is broken into vertical red→green→refactor slices; no speculative code.
- **Parallel specialised review**: code review, security review, and tech-debt review run concurrently.
- **Verified landing**: tests must pass and acceptance criteria must be verified before the PR is opened.
- **Persistent artefacts**: every phase produces a structured file committed alongside the code, making work resumable and auditable.

The skill is **tool- and model-agnostic**: it is written in plain Markdown and YAML. Any agent that can read files in a repository can follow it.

---

## Installation

This skill is published in the `japurcell/skills` repository under `skills/coding-task-workflow/`.

**Install via the provided script** (recommended):

```bash
git clone https://github.com/japurcell/skills.git
cd skills
./scripts/copilot-install.sh
```

This copies `skills/coding-task-workflow/` (and all other skills) to `~/.agents/skills/`. The agent runtime reads skills from that directory automatically.

**Manual install**:

```bash
cp -r skills/coding-task-workflow ~/.agents/skills/
```

**Verify installation**:

```bash
ls ~/.agents/skills/coding-task-workflow/
# Should list: SKILL.md  README.md  references/
```

Once installed, invoke the skill by name in any supported agent tool:

```
Use the coding-task-workflow skill to implement [feature/bug/spec].
```

---

## How the workflow works

The workflow has 12 phases (Phase 0 is optional). Each phase produces at least one artefact file. Gates between phases are explicit — the agent must not proceed until a gate condition is satisfied.

```
Phase 0  Bootstrap (optional)       — generates repo-local override files
Phase 1  Intake                     — structured work-item capture
Phase 2  Worktree setup             — git isolation
Phase 3  Codebase exploration  ──┐  — parallel subagents
Phase 4  Online research       ──┘  — parallel subagents
Phase 5  Clarification              — human gate (Gate C) if needed
Phase 6  Plan                       — Gate D (human approval)
Phase 7  TDD task graph            — Gate E (tests defined)
Phase 8  Implementation             — TDD red→green→refactor
Phase 9  Review                ──┐  — parallel specialised subagents
Phase 10 Verification          ──┘  — Gate F (all checks pass)
Phase 11 Commit / Push / PR        — conventional commits + PR creation
```

Full phase specifications: [`references/workflow.md`](references/workflow.md)
Stop-gate definitions: [`references/stop-gates.md`](references/stop-gates.md)
Sub-agent delegation rules: [`references/delegation-rules.md`](references/delegation-rules.md)

---

## How bootstrap works

The bootstrap phase (Phase 0) can be run independently on any repository to generate or update **repo-local override files** that tailor the workflow to that specific codebase.

The agent inspects likely signals in the target repo:

| Signal | What is inferred |
|--------|-----------------|
| `README.md` | Project purpose, tech stack, quick-start |
| `AGENTS.md` / `COPILOT.md` | Existing agent hints, conventions |
| `CONTRIBUTING.md` | Branch naming, PR process, code style |
| `package.json` / `pyproject.toml` / `go.mod` / `Cargo.toml` | Dependency ecosystem, scripts |
| `Makefile` | Build and test targets |
| `.github/workflows/*.yml` | CI commands for test, lint, typecheck, build |
| `docs/` | Architecture docs, ADRs, runbooks |
| `.eslintrc*` / `.flake8` / `rustfmt.toml` | Linting config and rules |
| Lockfiles | Exact dependency versions |

The agent **links/references existing docs** rather than duplicating them. It only writes new content where no existing doc covers the topic.

Each generated override file records:
- **source**: `canonical-doc | config-derived | ci-derived | inferred`
- **confidence**: `high | medium | low`
- **evidence**: the file or signal it was derived from

Full bootstrap specification: [`references/bootstrap.md`](references/bootstrap.md)

---

## Repo-local files generated in target repos

All generated files live under `.coding-workflow/` in the **target** repository.

### Override files (from Bootstrap)

Located at `.coding-workflow/overrides/`:

| File | Purpose |
|------|---------|
| `repo-inventory.yaml` | Tech stack, languages, frameworks, key directory paths |
| `doc-sources.md` | Pointers to existing docs — avoids duplication |
| `test-commands.yaml` | Exact test, lint, typecheck, and build commands |
| `repo-policy.md` | Branch naming, PR process, code-style rules, contribution gates |
| `architecture-notes.md` | High-level architecture, key modules, data-flow, patterns |
| `agent-hints.md` | Gotchas, known traps, environment quirks, agent-specific guidance |

### Per-work-item artefacts

Located at `.coding-workflow/work/<slug>/`:

| File | Phase | Purpose |
|------|-------|---------|
| `00-intake.md` | 1 | Work-item description, classification, acceptance criteria |
| `01-worktree.md` | 2 | Worktree path, branch, base commit |
| `02-exploration/summary.md` | 3 | Codebase findings and patterns |
| `02-exploration/files.csv` | 3 | Relevant files with reasons |
| `02-exploration/open-questions.md` | 3 | Questions for research/clarification |
| `03-research/findings.md` | 4 | Research answers with sources |
| `03-research/sources.md` | 4 | One row per source checked |
| `04-clarifications.md` | 5 | Human answers to blocking questions |
| `05-plan.md` | 6 | Implementation plan with file map |
| `06-task-graph.yaml` | 7 | TDD task DAG with phases |
| `07-implementation-log.md` | 8 | Slice-by-slice implementation log |
| `08-review/code-review.md` | 9 | Code review findings |
| `08-review/security-review.md` | 9 | Security review findings |
| `08-review/tech-debt.md` | 9 | Tech-debt findings |
| `09-verification.md` | 10 | Pass/fail per acceptance criterion |
| `10-pr.md` | 11 | PR number, URL, follow-up items |

Templates for all artefacts: [`references/templates/`](references/templates/)

---

## GitHub issue and PR integration

The skill uses a parent-issue / sub-issue hierarchy to make the order of operations visible in GitHub.

```
Parent issue: #N  [agent:parent]  Feature / bug / spec
  Sub-issue:  #N+1 [phase:exploration]  Codebase exploration
  Sub-issue:  #N+2 [phase:research]     Online research
  Sub-issue:  #N+3 [phase:plan]         Implementation plan
  Sub-issue:  #N+4 [phase:implement]    Task: <slice name>
  Sub-issue:  #N+5 [phase:implement]    Task: <slice name>
  Sub-issue:  #N+6 [phase:review]       Code / security / tech-debt review
  Sub-issue:  #N+7 [phase:verify]       Verification
```

Labels applied automatically: see [`references/issue-hierarchy.md`](references/issue-hierarchy.md).

The PR body links to the parent issue and to the artefact directory so reviewers can trace every decision.

---

## Example usage scenarios

### 1 — Starting from a feature description

```
Use the coding-task-workflow skill.
WORK_ITEM: Add a retry mechanism to the HTTP client with exponential backoff and jitter.
              Cap retries at 5 attempts. Retry on 429, 500, 502, 503, 504.
```

What happens: the agent classifies as `feature`, creates a slug, opens a parent issue, explores the existing HTTP client, researches backoff algorithms and language-idiomatic patterns, writes a plan, builds a TDD task graph (write test for single retry → write test for max retries → implement → add jitter → refactor), implements with three red→green→refactor slices, runs parallel review agents, verifies, and opens a PR.

---

### 2 — Starting from a bug report

```
Use the coding-task-workflow skill.
WORK_ITEM: Bug: pagination returns duplicate records when total_count is a multiple of page_size.
              Reproducible with page_size=10, total_count=20.
```

What happens: classified as `bug`, Light track exploration (one agent focused on the pagination logic), research phase checks for known off-by-one patterns, no clarification needed, plan proposes adding a regression test first, task graph has one RED slice (failing regression test), one GREEN slice (fix), one REFACTOR slice (clean up pagination helper), review agents check for similar bugs elsewhere, verification confirms reproduction script no longer fails.

---

### 3 — Starting from a detailed spec

```
Use the coding-task-workflow skill.
WORK_ITEM: /path/to/specs/auth-refresh-token.md
```

What happens: agent reads the spec file, extracts acceptance criteria automatically, skips most clarification (spec is detailed), creates a task graph directly from the spec's requirements, implements using TDD slices one per acceptance criterion.

---

### 4 — Bootstrapping repo overrides only

```
Use the coding-task-workflow skill.
BOOTSTRAP: only
```

What happens: Phase 0 only. Agent inspects the repo, infers tech stack, writes or updates all six override files in `.coding-workflow/overrides/`, commits with message `chore: bootstrap coding-workflow overrides`. No GitHub issue created. Takes ~2–5 minutes depending on repo size.

---

### 5 — Resuming an existing work item

```
Use the coding-task-workflow skill.
RESUME: 2026-04-23-add-retry-mechanism
```

What happens: agent reads the artefact directory for that slug, determines the last completed phase from artefact existence and frontmatter status fields, resumes from the next incomplete phase. Useful after an interrupted session or when handing off to a different agent.

---

### 6 — A repo with strong existing docs

```
Use the coding-task-workflow skill.
WORK_ITEM: Implement the user-preferences API described in docs/api/user-preferences.md
```

What happens: Bootstrap phase detects `docs/api/` and `CONTRIBUTING.md` already exist; `doc-sources.md` links to them rather than duplicating content. Plan phase references the spec directly. Exploration is lighter because architecture notes are already available. The agent asks fewer clarifying questions because the spec and docs answer most of them.

---

### 7 — A repo with weak or no docs

```
Use the coding-task-workflow skill.
WORK_ITEM: Add dark-mode support to the settings panel.
```

(Repository has no AGENTS.md, no CONTRIBUTING.md, minimal README.)

What happens: Bootstrap phase runs automatically (missing override files detected). Agent inspects `package.json`, CI workflows, and source tree to build `repo-inventory.yaml`, `test-commands.yaml`, and `architecture-notes.md` from scratch with `source: inferred` and `confidence: medium`. Exploration phase uses Deep track (3 parallel agents) to compensate for missing docs. Clarification phase asks the human about design-system conventions and storage approach for the preference.

---

### 8 — Issue-backed execution

```
Use the coding-task-workflow skill.
ISSUE: 42
WORK_ITEM: (read from issue body)
```

What happens: agent reads the GitHub issue body, extracts the description and any structured `## Machine Data` block, sets the work item from the issue. All sub-issues are linked as children of #42. PR references `Closes #42`.

---

### 9 — Workflow without GitHub issue creation

```
Use the coding-task-workflow skill.
WORK_ITEM: Refactor the UserService to use the repository pattern.
ISSUE: none
```

What happens: all artefacts are written to `.coding-workflow/work/<slug>/` as usual. No GitHub issues or sub-issues are created. PR body includes the artefact path instead of issue links. Useful in repos where issue tracking is managed externally.

---

### 10 — Implementing from an existing plan

```
Use the coding-task-workflow skill.
RESUME: 2026-05-01-repository-pattern-refactor
```

The artefact directory already contains `05-plan.md` with status `approved`. Agent detects Gate D is already satisfied, jumps directly to Phase 7 (task graph), and proceeds from there.

---

### 11 — Security-sensitive change

```
Use the coding-task-workflow skill.
WORK_ITEM: Replace the legacy MD5 password hashing with Argon2id.
```

What happens: research phase specifically checks OWASP Password Storage Cheat Sheet and the Argon2 RFC. Plan phase includes a migration strategy (dual-hash period for existing users). Security review agent is promoted to highest priority. Tech-debt agent flags any other weak-hashing usages found in the same pass. Verification phase includes a manual check that the old MD5 path is fully removed.

---

### 12 — Large cross-cutting change

```
Use the coding-task-workflow skill.
WORK_ITEM: Migrate all API responses from a flat JSON structure to JSON:API 1.1 spec.
```

What happens: Deep track exploration (3 agents covering controllers, serialisers, and tests). Research phase queries the JSON:API spec and any existing migration guides. Plan decomposes into 6 implementation slices. Task graph has 12 tasks. Implementation uses 3 parallel subagent groups for the three modules. Code-review agents are partitioned by module (non-overlapping). Verification runs the full test suite plus a smoke test against a running instance.

---

## Reference files

| File | Description |
|------|-------------|
| [`references/workflow.md`](references/workflow.md) | Full phase-by-phase workflow specification |
| [`references/stop-gates.md`](references/stop-gates.md) | Gate conditions, exit criteria, and failure handling |
| [`references/delegation-rules.md`](references/delegation-rules.md) | When and how to use subagents for each phase |
| [`references/artifact-schema.md`](references/artifact-schema.md) | YAML frontmatter schema and artefact format rules |
| [`references/issue-hierarchy.md`](references/issue-hierarchy.md) | GitHub issue hierarchy, labels, and body format |
| [`references/bootstrap.md`](references/bootstrap.md) | Full bootstrap / override-synthesis specification |
| [`references/templates/`](references/templates/) | Templates for all per-work-item artefacts and repo-local override files |
