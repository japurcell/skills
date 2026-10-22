---
name: meditate
description: Audit and evolve the brain vault - prune outdated content, discover cross-cutting principles, review skills for structural encoding opportunities. Triggers on "meditate", "audit the brain", "prune brain", "review skills", "consolidate notes", "prune notes".
disable-model-invocation: true
---

# Meditate

## Autonomous Session Mode

When running non-interactively:

- Apply all high-confidence changes autonomously. For ambiguous or risky changes (brain file deletions, principle rewrites), file a todo instead.
- Commit only when the user authorizes it; follow the repository commit workflow.

**Quality bar:** A note earns its place by being **high-signal** (The agent would reliably get this wrong without it), **high-frequency** (comes up in most sessions or most tasks of a type), or **high-impact** (getting it wrong causes significant damage or wasted work). Everything else is noise. A lean, precise brain outperforms a comprehensive but bloated one.

## Process

Track progress with the available planning tools or a short checklist.

### 1. Build snapshots

Use Python 3.12+ to create a temporary directory and run the bundled helper. Replace `<skill-path>` with this skill's directory:

```python
from pathlib import Path
import subprocess
import sys
import tempfile

temporary = Path(tempfile.mkdtemp(prefix="meditate-"))
for directory, name in [("brain", "brain-snapshot.md"),
                        (".agents/skills", "skills-snapshot.md")]:
    subprocess.run([sys.executable, "<skill-path>/scripts/snapshot.py",
                    directory, str(temporary / name)], check=True)
print(temporary)
```

Files are delimited with `=== path/to/file.md ===` headers. Retain the printed directory path and pass actual snapshot paths to reviewers. Keep it until the review finishes.

### 2. Auditor (blocking - its report feeds step 3)

Use an available general analysis subagent, or perform a bounded local review when delegation is unavailable. Read [agent prompts](references/agent-prompts.md) for the auditor and reviewer specifications. Inputs: brain snapshot, auto-memory path when present, AGENTS.md path.

Audits brain notes, AGENTS.md, and auto-memory for staleness, redundancy, low-value content, verbosity, and orphans. Returns a categorized report.

**Early-exit gate:** If the auditor finds fewer than 3 actionable items, skip step 3 and go directly to step 4.

### 3. Reviewer (after auditor completes)

Use one available general analysis subagent, or continue locally when delegation is unavailable. Use the reviewer specification from the agent prompts. Inputs: brain snapshot, skills snapshot, auditor report, `brain/principles.md`.

Combines three concerns in a single pass:

- **Synthesis**: Proposes missing Markdown links, flags principle tensions, suggests clarifications.
- **Distillation**: Identifies recurring patterns that reveal unstated principles. New principles must be (1) independent, (2) evidenced by 2+ notes, (3) actionable.
- **Skill review**: Cross-references skills against brain principles. Finds contradictions, missed structural enforcement, redundant instructions. Audits description frontmatters for context bloat.

### 4. Review reports

Present the user with a consolidated summary using the report template from the agent prompts.

### 5. Route skill-specific learnings

Check all reports for findings that belong in skill files, not `brain/`. Update the skill's SKILL.md or references/ directly. Read the skill first to avoid duplication.

### 6. Apply changes

Apply all changes directly. The user reviews the diff.

- **Outdated notes**: Update or delete
- **Redundant notes**: Merge into the stronger note, delete the weaker
- **Low-value notes**: Delete
- **Verbose notes**: Condense in place
- **New connections**: Add file-relative Markdown links
- **Tensions**: Reword to clarify boundaries
- **New principles**: Only from the distillation section, only if genuinely independent. Write brain files and update `brain/principles.md`
- **Merge principles**: Look for principles that are subsets or specific applications of each other - merge the narrower into the broader and pick a name that captures the combined insight
- **Bloated skill descriptions**: Tighten frontmatter descriptions - cut what the agent can infer, keep only distinctive triggers and purpose
- **AGENTS.md issues**: Rewrite or delete
- **Stale memories**: Delete or rewrite

### 7. Housekeep

Activate the `brain` skill to maintain curated navigation and reconcile the root inventory, using manual indexing if hooks are unavailable. Remove only the temporary directory created in step 1 after all reviewers finish, using `shutil.rmtree` in Python with that exact retained path.

## Summary

```
## Meditate Summary
- Pruned: [N notes deleted, M condensed, K merged]
- Extracted: [N new principles, with one-line + evidence count each]
- Skill review: [N findings, M applied]
- Housekeep: [state files cleaned]
```
