# Technical Debt Dedup Report

## Scope Analyzed
- Current uncommitted diff and recently changed files in this session.
- Candidate duplicates across source, tests, scripts, and config.
- Cross-file repetition patterns independent of language/framework.

## Findings
1. Exact duplicate
- Repeated boilerplate blocks in eval metadata scaffolding.

2. Near duplicate
- Similar validation and summarization steps repeated with minor wording changes.

3. Reimplementation
- Local inline checks that duplicate existing utility patterns in neighboring skills.

## Refactor Actions
- Consolidate repeated metadata scaffolding through one reusable template.
- Factor shared validation/reporting steps into a reusable helper section.
- Keep project structure intact; avoid introducing new top-level abstractions.

## Validation Plan
- Targeted check: validate all `eval_metadata.json` files parse and include required keys.
- Broad check: run repository-relevant lint/test/type/build command set for the touched area.
- Confirm no framework-specific assumptions were introduced.
