---
name: task-wave
description: Plans non-trivial repository work as short, dependency-ordered waves with explicit validation and stop points. Use when a request spans several dependent tasks, files, or verification steps, or when a weaker model needs a literal wave-by-wave execution order instead of vague advice.
---

# Task Wave

## Overview

Use this skill to break multi-step repo work into small waves that can be finished and verified in order.

Each wave should say exactly what to do, which files or surfaces it touches, and what command proves the wave is complete.

## When to Use

- The task has dependencies, multiple files, or separate validation steps.
- You need a short execution plan that weaker models can follow without guessing.
- You want to separate setup, implementation, and validation instead of mixing them into one blob.
- Not for one-step or single-file tasks that can be completed directly.

## Workflow

1. **Decide whether waves are needed**
   - If the work is one atomic task, do not invent waves.
   - If later work depends on earlier work, create waves.

2. **Split the work into 2-5 waves**
   - Put prerequisite work first.
   - Put independent work in the same wave only when it can really happen in parallel.
   - Give each wave a short goal.

3. **Make every wave literal**
   - Name the exact files or directories to inspect or edit.
   - State the concrete action, not "figure it out" or "finish up".
   - Add the exact validation command for that surface.

4. **Finish one wave before starting the next**
   - Do the wave.
   - Run its validation.
   - Record what is done and what the next wave depends on.

5. **Close with the next action**
   - Say whether the task is complete or which wave is next.
   - If validation is still missing, say exactly what remains.

## Specific Techniques

### Recommended wave format

Use this compact structure:

```text
Wave 1 - goal
- Files: path/a, path/b
- Do: concrete action
- Validate: exact repo command
- Exit: what must be true before Wave 2
```

### Validation selection for this repository

- Skill definition edits: `python3 skills/skill-creator/scripts/quick_validate.py <skill-path>`
- Skill-local grader edits: `python3 -m py_compile <skill-path>/evals/grade_benchmark.py`
- Benchmark grading runs: `python3 <skill-path>/evals/grade_benchmark.py skills/<skill-name>-workspace/iteration-<N>`
- Copilot installer edits: `bash -n scripts/copilot-install.sh`
- Addy installer edits: `bash -n scripts/addy-install.sh && bash scripts/test-addy-install.sh`
- After promoting repo-source skill changes: `./scripts/copilot-install.sh`

Do not default to `npm test`, `npm run build`, or "run the usual validation". This repository uses narrow commands tied to the edited surface.

## Common Rationalizations

| Rationalization | Reality |
| --- | --- |
| "I can keep this as one big wave." | Large mixed waves make weaker models skip dependencies and verification. |
| "I'll just say run the normal tests." | This repo does not have one generic test command; name the surface-specific command. |
| "These steps are obvious, so I can leave them implied." | Weaker models follow explicit files, commands, and stop points more reliably than implied workflow. |

## Red Flags

- The plan includes vague steps like "do the tasks" or "finish up".
- A wave mixes unrelated work with no dependency reason.
- Validation uses `npm test`, `npm run build`, or other invented repo-wide commands.
- The plan starts a later wave before saying how the current wave is complete.

## Verification

- [ ] Waves are used only when the work is truly multi-step.
- [ ] Each wave names concrete files, actions, and an exit condition.
- [ ] Each wave uses an exact repo command for validation, or explicitly says why no command applies.
- [ ] Dependencies and parallel work are explicit instead of implied.
- [ ] The final output says what is done now and what happens next.
