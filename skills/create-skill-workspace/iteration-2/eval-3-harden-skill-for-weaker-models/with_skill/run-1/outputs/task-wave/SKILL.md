---
name: task-wave
description: Plans non-trivial repository work as short, dependency-ordered waves with exact files, validation commands, and exit conditions. Use when a task spans multiple dependent edits, handoff steps, or verification surfaces; when rewriting a vague plan into a literal execution sequence; or when a weaker model needs explicit stop points instead of implied workflow.
---

# Task Wave

## Overview

Use this skill to turn a multi-step task into a short sequence of waves that can be executed and verified in order.

The goal is not to add ceremony. The goal is to remove guessing: every wave should say exactly what gets touched, how completion is proven, and what unlocks the next wave.

## When to Use

- The task spans multiple files, commands, or checkpoints that depend on one another.
- You are handing work to a weaker model that follows literal instructions better than implied sequencing.
- You need to rewrite a vague task list into an execution order with exact files and validation.
- You need to separate implementation work from refresh, packaging, or grading steps.
- Not for one-step work that can be done directly without a dependency chain.
- Not for brainstorming or high-level strategy where the next action is still unclear.

## Workflow

1. **Decide whether waves are justified**
   - If the work is a single atomic change, say that waves are not needed and stop.
   - If later work depends on earlier work, use waves.

2. **Split the task into 2-5 dependency-ordered waves**
   - Put prerequisite reading, editing, validation, and refresh work in the order they must happen.
   - Group work in the same wave only when it can genuinely be completed together.
   - Give each wave one short goal.

3. **Make each wave literal**
   - Name the exact files or directories involved.
   - Say what to do with action verbs like `edit`, `update`, `add`, `validate`, or `refresh`.
   - Name the exact validation command for that surface, or say why no command applies.
   - Add an exit condition that explains what must be true before the next wave starts.

4. **Use the output format directly**
   - For multi-wave work, write each wave in this shape:

   ```text
   Wave 1 - short goal
   - Files: path/a, path/b
   - Do: exact action
   - Validate: exact command or "none"
   - Exit: concrete done state
   ```

   - For work that should not be split, answer in this shape:

   ```text
   No waves needed.
   - Files: path/to/file
   - Do: exact action
   - Validate: exact command or "none"
   - Exit: concrete done state
   ```

5. **Close with the next action**
   - End by saying either `Next: Wave N` or `Complete.`
   - If validation or refresh still remains, name that step explicitly instead of implying it.

## Specific Techniques

### Wave-building rules

- Prefer 2-4 waves. More than that usually means the plan is too granular.
- Do not hide validation in a generic final wave if earlier waves can fail independently.
- If two edits touch different files but must land together before one validation command makes sense, keep them in the same wave and say why.
- Replace vague phrases like `figure out`, `handle this`, `run the usual tests`, and `finish up` with literal actions.

### Validation selection for this repository

- Skill definition edits: `python3 skills/skill-creator/scripts/quick_validate.py skills/<skill-name>`
- Skill-local grader edits: `python3 -m py_compile skills/<skill-name>/evals/grade_benchmark.py`
- Benchmark grading runs: `python3 skills/<skill-name>/evals/grade_benchmark.py skills/<skill-name>-workspace/iteration-<N>`
- Copilot installer edits: `bash -n scripts/copilot-install.sh`
- Addy installer edits: `bash -n scripts/addy-install.sh && bash scripts/test-addy-install.sh`
- After promoting repo-source skill changes: `./scripts/copilot-install.sh`

There is no single repo-wide `npm test` or `npm run build` command here. Pick the narrow command that matches the edited surface.

### What a good wave plan sounds like

- It reads like a handoff another agent could execute without reopening the task for clarification.
- It tells the reader why a later wave cannot start yet.
- It makes the stop point visible, which matters most when the task crosses source edits, benchmark files, and refresh steps.

## Common Rationalizations

| Rationalization | Reality |
| --- | --- |
| "I can keep everything in one big wave." | Mixed waves hide dependencies and make it easy to skip validation. |
| "The commands are obvious, so I can just say run the usual checks." | This repo relies on narrow surface-specific commands, not a generic test runner. |
| "These are tiny edits, so I do not need exit conditions." | Exit conditions are what keep weaker models from starting the next step too early. |
| "I will add the exact files later after I inspect the repo." | If the files are already known from the task, include them now so the handoff is executable. |

## Red Flags

- The plan uses vague verbs like `do the tasks`, `figure it out`, or `finish up`.
- A later wave starts before the current wave says how it is complete.
- Validation falls back to `npm test`, `npm run build`, or another invented repo-wide command.
- The plan creates waves for a one-line, one-file change that should be done directly.
- The final answer never says whether the next action is another wave or completion.

## Verification

- [ ] Waves are used only when the work is actually multi-step or dependency-ordered.
- [ ] Every wave names concrete files, actions, validation, and an exit condition.
- [ ] Validation commands match this repository instead of generic npm language.
- [ ] The plan makes dependencies explicit instead of implying them.
- [ ] The answer ends with a clear next action or completion state.
