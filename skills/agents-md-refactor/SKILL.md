---
name: agents-md-refactor
description: Refactor AGENTS.md and related instruction files into a progressive-disclosure structure. Use this skill whenever the user asks to clean up, simplify, reorganize, split, or standardize AGENTS.md or instruction docs (including root and scoped AGENTS files), especially when they want essentials in root and detailed rules moved into linked topic files.
---

# AGENTS.md Refactor Skill

Refactor AGENTS-style instruction docs so they are easier to load and maintain.

## Goal

Produce a minimal root AGENTS.md that contains only globally essential guidance, then move all specialized guidance into linked, topic-specific files.

## Operating Principles

1. Keep root AGENTS.md short and always-load safe.
2. Prefer actionable rules over vague advice.
3. Preserve scope boundaries (root vs subdirectory AGENTS files).
4. Avoid duplicate guidance across files; link instead.
5. Do not silently resolve conflicts between instructions.

## Required Workflow

### 1. Collect instruction sources

- Read root AGENTS.md and any scoped AGENTS.md files.
- Read currently linked instruction docs if they exist.
- Build a quick map of where each rule currently lives.

### 2. Find contradictions first

- Identify conflicts where two rules cannot both be followed.
- Present each contradiction clearly.
- Ask the user which version to keep.

If contradictions exist, pause structural edits until the user chooses a direction, unless they explicitly ask you to apply a default policy.

### 3. Extract root essentials

Keep only guidance that is relevant to nearly every task:

- One-sentence project description
- Package manager only if non-default or easily confused
- Non-standard build/typecheck/test commands
- One or two universal workflow constraints that truly apply everywhere

Move all domain-specific rules out of root.

### 4. Group and split remaining guidance

Create topic files for specialized content. Typical groups:

- Workflow
- Frontend conventions
- Backend conventions
- Validation/testing
- Environment/secrets
- Git/release process

Use concise filenames and keep each file focused on one topic.

### 5. Produce final structure

Generate:

- Minimal root AGENTS.md with links
- Updated scoped AGENTS.md files where needed
- New/updated topic docs
- Suggested docs tree if folders do not exist yet

### 6. Flag deletion candidates

Call out instructions that are:

- Redundant (already covered elsewhere)
- Non-actionable (too vague)
- Obvious boilerplate that adds no behavioral guidance

## Output Contract

When reporting results, use this structure:

### A. Contradictions

For each contradiction:

1. Conflict summary
2. Source A (file + short quote)
3. Source B (file + short quote)
4. Question: "Which version should I keep?"

### B. Root Essentials Draft

- Show proposed root AGENTS.md content.

### C. Grouped Files

- List each topic file and what rules it now owns.

### D. Suggested Folder Structure

- Show a tree-style layout.

### E. Deletion Candidates

- List candidate text, reason, and original location.

## Quality Bar

- Root AGENTS.md should usually stay under ~120 lines.
- Every linked file should have a clear purpose and no mixed scopes.
- No orphan links.
- No duplicated rule text unless duplication is explicitly justified.
