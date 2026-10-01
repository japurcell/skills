# Skill Audit Inventory Baseline

This read-only inventory was gathered on 2026-10-01 to scope the audit. It is a routing baseline, not a completed authoring audit.

## Maintained entry points

`skills/` contains 55 top-level directories with `SKILL.md`. `.agents/skills/` contains five: `clean-agent-docs`, `exec-plans`, `ingest-source`, `okf-authoring`, and `update-agent-docs`. The user's idea includes both roots. No symlinks were found in either root, and no `skills/archive/` directory exists in this checkout.

There are 10 sibling benchmark workspaces under `skills/`: `architecture-design-contest`, `code-review`, `commit`, `create-skill`, `handoff`, `official-sources`, `okf-authoring`, `prd-to-tasks`, `self-improve`, and `techdebt`, each with the `-workspace` suffix. Recursive discovery finds 72 `SKILL.md` files under `skills/`; nested snapshots, generated outputs, and the two `create-skill` fixture skills must not inflate the 55 maintained entry points. See `.agents/memory/ARCHITECTURE.md:54` and `README.md:49` for source and installation boundaries.

## Existing evaluation coverage

Sixteen of the 55 primary skills contain `evals/evals.json`: `adversarial-review`, `architecture-design-contest`, `code-review`, `commit`, `create-skill`, `dotnet`, `dotnet-upgrade`, `explore`, `handoff`, `harness-analysis`, `improve-skill`, `official-sources`, `prd-ralph-loop`, `self-improve`, `spec-to-tasks`, and `techdebt`.

Twelve contain `evals/grade_benchmark.py`: `adversarial-review`, `code-review`, `commit`, `create-skill`, `explore`, `handoff`, `harness-analysis`, `improve-skill`, `official-sources`, `prd-ralph-loop`, `self-improve`, and `spec-to-tasks`. The repository-local `okf-authoring` skill has another eval set under `.agents/skills/`.

File presence does not prove evaluation quality, coverage, or pass state. Existing conventions are in `.agents/instructions/skills.md:24` and `.agents/memory/testing/skills.md:7`. Preserve `dotnet-upgrade` document-only review scope.

## Import provenance and constraints

`.addy-skills` names four Addy-derived skills: `addy-code-review-and-quality`, `addy-code-simplification`, `addy-performance-optimization`, and `addy-security-and-hardening`. `scripts/addy-install.sh` imports from a sibling `addy-agent-skills` checkout and prefixes names.

`scripts/import-skill-repos.sh` names additional sources including `anthropics/claude-plugins-official`, `mattpocock/skills`, `JuliusBrussee/caveman`, `humanlayer/skills`, `addyosmani/web-quality-skills`, and the `anthropics/show-me` plugin. Check actual importer mappings before deciding whether a local edit survives refresh. The maintained `skill-creator` bundle itself has Claude-specific assumptions requiring compatibility assessment.

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
