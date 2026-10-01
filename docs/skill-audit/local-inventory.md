# Skill Audit Inventory Baseline

This read-only inventory was gathered on 2026-10-01 to scope the audit. It is a routing baseline, not a completed authoring audit.

## Maintained entry points

`skills/` contains 55 top-level directories with `SKILL.md`. `.agents/skills/` contains five: `clean-agent-docs`, `exec-plans`, `ingest-source`, `okf-authoring`, and `update-agent-docs`. The user's idea includes both roots. No symlinks were found in either root, and no `skills/archive/` directory exists in this checkout.

There are 10 sibling benchmark workspaces under `skills/`: `architecture-design-contest`, `code-review`, `commit`, `create-skill`, `handoff`, `official-sources`, `okf-authoring`, `prd-to-tasks`, `self-improve`, and `techdebt`, each with the `-workspace` suffix. Recursive discovery finds 72 `SKILL.md` files under `skills/`; nested snapshots, generated outputs, and the two `create-skill` fixture skills must not inflate the 55 maintained entry points. See `.agents/memory/ARCHITECTURE.md:54` and `README.md:49` for source and installation boundaries.

## Current audit scope

The human narrowed this effort on 2026-10-01: exclude imported skills and review the remaining candidates. The [ownership decision](tickets/decide-skill-ownership-and-import-handling.md#resolution) supersedes the original all-skills scope. The current scripts map 23 published entry points to import sources; exclude those entry points using [the import evidence](import-ownership-evidence.md). This leaves 32 published candidates plus the five repository-local candidates, for 37 total.

The published candidates are: adversarial-review, agents-md-improver, architecture-design-contest, code-modernization, code-review, code-simplify, commit, create-agentsmd, create-skill, delegate-to-subagents, dotnet, dotnet-ui-app, dotnet-upgrade, execplan-implement, explain-your-thinking, explore, fixing-accessibility, gh-cli, guidance-review, handoff, harness-analysis, improve-repo-harness, improve-skill, official-sources, prd, prd-ralph, prd-ralph-loop, self-improve, spec-to-tasks, subagent-model-router, techdebt, to-issues.

Remove additional imported entry points when clear evidence establishes their origin. An absent importer mapping does not prove repository authorship, but unknown historical origin alone does not block reviewing a remaining candidate. Do not recover historical provenance or build a lasting ledger. Check shared resources only where they are dependencies of included skills; excluded bundles are not audit or improvement targets.

## Existing evaluation coverage

Sixteen of the 55 primary skills contain `evals/evals.json`: `adversarial-review`, `architecture-design-contest`, `code-review`, `commit`, `create-skill`, `dotnet`, `dotnet-upgrade`, `explore`, `handoff`, `harness-analysis`, `improve-skill`, `official-sources`, `prd-ralph-loop`, `self-improve`, `spec-to-tasks`, and `techdebt`.

Twelve contain `evals/grade_benchmark.py`: `adversarial-review`, `code-review`, `commit`, `create-skill`, `explore`, `handoff`, `harness-analysis`, `improve-skill`, `official-sources`, `prd-ralph-loop`, `self-improve`, and `spec-to-tasks`. The repository-local `okf-authoring` skill has another eval set under `.agents/skills/`.

File presence does not prove evaluation quality, coverage, or pass state. Existing conventions are in `.agents/instructions/skills.md:24` and `.agents/memory/testing/skills.md:7`. Preserve `dotnet-upgrade` document-only review scope.

## Import provenance and constraints

`.addy-skills` records four unprefixed source names: `code-review-and-quality`, `code-simplification`, `performance-optimization`, and `security-and-hardening`. `scripts/addy-install.sh` imports from a sibling `addy-agent-skills` checkout and prefixes destination names with `addy-`. All four mapped destination entry points exist.

`scripts/import-skill-repos.sh` names additional sources: `anthropics/claude-plugins-official`, `mattpocock/skills`, `JuliusBrussee/caveman`, `humanlayer/skills`, and `addyosmani/web-quality-skills`. The configured `show-me` source is `humanlayer/skills`, not `anthropics/show-me`. [Import and packaging evidence](import-ownership-evidence.md) records the exact mappings, destructive or overlay refresh behavior, and source-history limits. This evidence establishes exclusions rather than authorizing imported-skill improvements. The imported `skill-creator` bundle is excluded; included skills that depend on it receive only scoped dependency checks.

## Inventory delegation record

    subtask_id: skill-audit-inventory
    selected: {model: gpt-6-luna, reasoning_effort: medium}
    submitted: {model: gpt-6-luna, reasoning_effort: medium}
    executed: {model: unconfirmed, reasoning_effort: unconfirmed}
    runtime_limit: {value: 300 seconds, mechanism: parent elapsed-time checks and interruption}
    status: completed
    output_verified: true
    routing_compliant: true

The parent checked source-boundary and evaluation claims against loaded guidance. Enumeration was entrusted to the read-only explorer. No evaluation runs were performed.
