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
- **Session boundary before implementation**: the workflow hard-stops after Phase 7 and resumes in a fresh session for Phases 8–11.
- **TDD-first implementation**: work is broken into vertical red→green→refactor slices; no speculative code.
- **Parallel specialised review**: code review, security review, and tech-debt review run concurrently.
- **Verified landing**: tests must pass and acceptance criteria must be verified before the PR is opened.
- **Commit hygiene**: the final commit message ends with a blank-line-separated `Co-authored-by: NAME <EMAIL>` trailer block using the agent's own co-author identity.
- **Persistent artifacts**: Phase 0 writes repo-local override files; Phases 1–11 persist durable workflow state in GitHub issues and comments, making work resumable and auditable across agents.

The skill is **tool- and model-agnostic**: it is written in plain Markdown and YAML. Any agent that can read the repo and update GitHub issues can follow it.

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

The workflow has 12 phases (Phase 0 is optional). Phase 0 produces repo-local override files; Phases 1–11 produce GitHub-native artifacts. Gates between phases are explicit — the agent must not proceed until a gate condition is satisfied.

```
Phase 0  Bootstrap (optional)       — generates repo-local override files
Phase 1  Intake                     — structured work-item capture
Phase 2  Worktree setup             — git isolation
Phase 3  Codebase exploration  ──┐  — parallel subagents
Phase 4  Online research       ──┘  — parallel subagents
Phase 5  Clarification              — human gate (Gate C) if needed
Phase 6  Plan                       — Gate D (human approval)
Phase 7  TDD task graph            — Gate E (tests defined) + hard stop
Phase 8  Implementation             — TDD red→green→refactor after resume
Phase 9  Review                ──┐  — parallel specialised subagents
Phase 10 Verification          ──┘  — Gate F (all checks pass)
Phase 11 Commit / Push / PR        — conventional commits + PR creation
```

Full phase specifications: [`references/workflow.md`](references/workflow.md)
Stop-gate definitions: [`references/stop-gates.md`](references/stop-gates.md)
Sub-agent delegation rules: [`references/delegation-rules.md`](references/delegation-rules.md)

After Phase 7, the agent must stop and hand off a `RESUME=<slug>` command for a fresh session. This keeps the heavier implementation, review, verification, and landing work out of the earlier planning context window.
If the user asks to continue into implementation immediately, the workflow still stops and returns the resume handoff instead.

---

## How bootstrap works

The bootstrap phase (Phase 0) can be run independently on any repository to generate or update **repo-local override files** that tailor the workflow to that specific codebase.

The agent inspects likely signals in the target repo:

| Signal                                                      | What is inferred                             |
| ----------------------------------------------------------- | -------------------------------------------- |
| `README.md`                                                 | Project purpose, tech stack, quick-start     |
| `AGENTS.md` / `COPILOT.md`                                  | Existing agent hints, conventions            |
| `CONTRIBUTING.md`                                           | Branch naming, PR process, code style        |
| `package.json` / `pyproject.toml` / `go.mod` / `Cargo.toml` | Dependency ecosystem, scripts                |
| `Makefile`                                                  | Build and test targets                       |
| `.github/workflows/*.yml`                                   | CI commands for test, lint, typecheck, build |
| `docs/`                                                     | Architecture docs, ADRs, runbooks            |
| `.eslintrc*` / `.flake8` / `rustfmt.toml`                   | Linting config and rules                     |
| Lockfiles                                                   | Exact dependency versions                    |

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

| File                    | Purpose                                                           |
| ----------------------- | ----------------------------------------------------------------- |
| `repo-inventory.yaml`   | Tech stack, languages, frameworks, key directory paths            |
| `doc-sources.md`        | Pointers to existing docs — avoids duplication                    |
| `test-commands.yaml`    | Exact test, lint, typecheck, and build commands                   |
| `repo-policy.md`        | Branch naming, PR process, code-style rules, contribution gates   |
| `architecture-notes.md` | High-level architecture, key modules, data-flow, patterns         |
| `agent-hints.md`        | Gotchas, known traps, environment quirks, agent-specific guidance |

### Phase artifacts

Phase 0 still writes repo-local overrides. After that, the workflow keeps its durable per-work-item state in GitHub:

| Artifact | Phase | Durable location | Purpose |
| -------- | ----- | ---------------- | ------- |
| Parent issue | 1 | Parent issue body | Lightweight work-item index and current phase |
| Intake artifact | 1 | `phase:intake` child issue | Summary, classification, acceptance criteria, constraints |
| Worktree artifact | 2 | `phase:worktree` child issue | Worktree path, branch, base commit |
| Exploration summary | 3 | `phase:exploration` child issue | Codebase findings and anti-patterns |
| `files.csv` artifact | 3 | Artifact subissue under exploration | `files.csv` content in fenced `csv` |
| Open questions | 3–5 | Artifact subissue under exploration | Durable question ledger across research and clarification |
| Research findings | 4 | `phase:research` child issue | Research answers and decisions |
| `sources.md` artifact | 4 | Artifact subissue under research | One row per URL checked |
| Clarifications | 5 | `phase:clarification` child issue | Human answers and assumptions |
| Plan | 6 | `phase:plan` child issue | Approved implementation plan |
| Task graph | 7 | `phase:task-graph` child issue | YAML task graph in fenced `yaml` |
| Implementation progress | 8 | Comments on task issues | RED / GREEN / REFACTOR execution log |
| Review findings | 9 | `phase:review` child issue | Combined code / security / tech-debt review |
| Verification | 10 | `phase:verify` child issue | Automated checks and acceptance results |
| PR metadata | 11 | `phase:pr` child issue | PR number, URL, follow-up items |

Templates for GitHub issue artifacts: [`references/templates/`](references/templates/)

---

## GitHub issue and PR integration

The skill uses a parent-issue / sub-issue hierarchy to make the order of operations visible in GitHub.

```
Parent issue: #N  [agent:parent]  Feature / bug / spec
  Sub-issue:  #N+1 [phase:intake]         Intake artifact
  Sub-issue:  #N+2 [phase:worktree]       Worktree metadata
  Sub-issue:  #N+3 [phase:exploration]    Exploration summary
    Sub-issue: #N+3a [artifact]           files.csv
    Sub-issue: #N+3b [artifact]           open-questions
  Sub-issue:  #N+4 [phase:research]       Research findings
    Sub-issue: #N+4a [artifact]           sources.md
  Sub-issue:  #N+5 [phase:clarification]  Human answers and assumptions
  Sub-issue:  #N+6 [phase:plan]           Implementation plan
  Sub-issue:  #N+7 [phase:task-graph]     YAML task graph in issue body
    Sub-issue: #N+7a [phase:implement]    Task: <slice name>
    Sub-issue: #N+7b [phase:implement]    Task: <slice name>
  Sub-issue:  #N+8 [phase:review]         Code / security / tech-debt review
  Sub-issue:  #N+9 [phase:verify]         Verification
  Sub-issue:  #N+10 [phase:pr]            PR metadata
```

Labels applied automatically: see [`references/issue-hierarchy.md`](references/issue-hierarchy.md).

The PR body fixes the parent issue and leaves the GitHub issue tree as the durable decision record.

---

## Example usage scenarios

In the examples below, any implementation, review, verification, commit, or PR work happens only after the mandatory resume that follows Phase 7.

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

What happens: classified as `bug`, Light track exploration (one agent focused on the pagination logic), research phase checks for known off-by-one patterns, no clarification needed, plan proposes adding a regression test first, task graph creates one vertical slice for the bugfix, Phase 8 records the RED regression test result, GREEN fix, and REFACTOR cleanup as comments on that same task issue, review agents check for similar bugs elsewhere, and verification confirms the reproduction script no longer fails.

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

What happens: agent finds the parent issue and descendant phase/task issues by `work_id`, determines the last completed phase from issue closure state plus approval / implementation-log comments, and resumes from the next incomplete phase. Useful after an interrupted session or when handing off to a different agent.

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

What happens: agent reads the GitHub issue body, extracts the description and any structured `## Machine Data` block, and treats that content as the authoritative `WORK_ITEM`. A separate `phase:intake` child issue is still created under #42 so the structured intake artifact stays distinct from the lightweight parent issue. All later child issues are created as actual GitHub sub-issues of #42 (using the GitHub sub-issue mutation, not just a body reference). PR references `Fixes #42`.

---

### 9 — Repository without GitHub issue creation

```
Use the coding-task-workflow skill.
WORK_ITEM: Refactor the UserService to use the repository pattern.
ISSUE: none
```

What happens: Bootstrap can still run, but the workflow stops before Phase 1. This version of the skill requires GitHub issues for Phases 1–11 because they are the durable cross-agent record. The agent explains the blocker instead of silently falling back to local per-work-item markdown files.

---

### 10 — Implementing from an existing plan

```
Use the coding-task-workflow skill.
RESUME: 2026-05-01-repository-pattern-refactor
```

The plan issue is already approved and closed. Agent detects Gate D is already satisfied, jumps directly to Phase 7 (task graph), then hard-stops and tells the human to resume in a fresh session for implementation.

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

| File                                                               | Description                                                             |
| ------------------------------------------------------------------ | ----------------------------------------------------------------------- |
| [`references/workflow.md`](references/workflow.md)                 | Full phase-by-phase workflow specification                              |
| [`references/stop-gates.md`](references/stop-gates.md)             | Gate conditions, exit criteria, and failure handling                    |
| [`references/delegation-rules.md`](references/delegation-rules.md) | When and how to use subagents for each phase                            |
| [`references/artifact-schema.md`](references/artifact-schema.md)   | GitHub issue/comment machine-data schema and artifact format rules      |
| [`references/issue-hierarchy.md`](references/issue-hierarchy.md)   | GitHub issue hierarchy, labels, and body format                         |
| [`references/bootstrap.md`](references/bootstrap.md)               | Full bootstrap / override-synthesis specification                       |
| [`references/templates/`](references/templates/)                   | Templates for all per-work-item artifacts and repo-local override files |
