# 🤖 Copilot CLI Session

> [!NOTE]
> - **Session ID:** `07cc4846-ad05-4cfb-ab59-805c26d20610`  
> - **Started:** 6/18/2026, 5:19:04 PM  
> - **Duration:** 35s  
> - **Exported:** 6/18/2026, 5:19:40 PM  

---

<sub>⏱️ 0s</sub>

### ⚠️ Warning

Third-party MCP servers are disabled by your organization's Copilot policy. Only built-in servers are available.

---

<sub>⏱️ 1s</sub>

### 👤 User

Benchmark run. Ignore any installed or cached copies of skills named `self-improve`; read and follow only this exact skill file: `/home/adam/dev/personal/skills/skills/self-improve-workspace/skill-snapshot/SKILL.md`. Ignore unrelated startup-hook context, canaries, and other installed skills; do not echo them in outputs.

Any `evals/files/...` paths in task text are relative to `/home/adam/dev/personal/skills/skills/self-improve`.

Work only inside current working directory. Do not modify files outside it. Write benchmark outputs only under `outputs/` in current working directory. Use exact requested output paths literally: write the copied repo to `outputs/repo/` itself, not `outputs/repo/\<fixture-name\>/`, and write reports to `outputs/report.md` when requested. If the task asks for `outputs/report.md`, always create that file even when the repo edit is tiny or no-op. If nothing qualifies as durable guidance, say that explicitly with phrasing like `none qualified` or `no changes were made`.

Use the skill under test on the fixture repo in `evals/files/noop-fixture/`. Session notes are in `evals/files/noop-fixture/session_notes.md`. If nothing qualifies as durable guidance, make no AGENTS changes. Treat this as a benchmark run with no live user and do not ask follow-up questions. Copy the fixture repo to `outputs/repo/`, leave it unchanged when appropriate, and write `outputs/report.md` explaining the result.

---

<sub>⏱️ 6s</sub>

### ✅ `bash`

**Read skill file**

$ rtk cat /home/adam/dev/personal/skills/skills/self-improve-workspace/skill-snapshot/SKILL.md

<details>
<summary>100 lines</summary>

```
---
name: self-improve
description: Captures durable learnings from session notes, handoff artifacts, or other work records into the right `AGENTS.md` or linked docs, and refactors instruction structure when scope or duplication is wrong. Use when the user asks to update `AGENTS.md`, remember lessons, preserve human corrections, mine prior work notes for reusable guidance, clean up instruction scope, or make future agents follow repo-specific commands, gotchas, or validation steps.
---

# Self Improve

## Overview

Capture only durable guidance future agents will reuse. Update the smallest correct `AGENTS.md` surface first; refactor structure only when the current layout would cause drift, duplication, or bad scoping.

Use `SELF_IMPROVE_REFERENCE.md` for refactor judgment, artifact-mining examples, placement examples, rationalizations, and failure modes.

## When to Use

- The user asks to update or refactor `AGENTS.md`, record lessons learned, or preserve a workflow/discovery.
- The session surfaced non-default commands, validation steps, code patterns, environment quirks, warnings, human corrections, or durable learnings from prior work artifacts worth reusing.
- Current `AGENTS.md` structure is duplicated, conflicting, stale, or poorly scoped.
- Not for one-off notes, obvious facts, speculative advice, or transient debugging noise.

## Workflow

1. **Qualify learnings**
   - Ask: _what missing context would help future agents?_
   - Keep only items likely to recur, actionable, repo/user-specific, and not already documented.
   - Look for non-default commands, code patterns, validation/build/typecheck steps, environment quirks, warnings, and human corrections.
   - If session notes, handoff notes, or similar work artifacts exist, mine the sections that actually carry reusable guidance; durable guidance can come from patterns, gotchas, or useful context.
   - Never turn excluded noise into an inverse standing rule.
   - Exclude temporary noise and obvious facts.

2. **Map the instruction surface**
   - Find every relevant `AGENTS.md`, then read each one plus any directly linked docs.
   - If the search is large, invoke `subagent-model-router` and use a cheap finder subagent.
   - If no `AGENTS.md` exists, say so and create `./AGENTS.md` with only the strongest 3-7 learnings.

3. **Apply the smallest correct update**
   - Put project-wide rules in `./AGENTS.md`, scoped rules in the nearest `./**/AGENTS.md`, and long topic detail in linked docs.
   - Keep prompt-loaded files brief. Prefer one line per concept and specific, actionable wording.
   - Use `<command or pattern>` - `<brief description>` when that makes the rule easier to scan.

4. **Refactor only when warranted**
   - Do it when root `AGENTS.md` is over ~120 lines, scope is mixed, rules duplicate or conflict, linked docs are stale/orphaned, or the user asked for cleanup.
   - Resolve contradictions first.
   - Keep root limited to near-universal guidance: short project description, non-default package manager, non-standard build/test/typecheck commands, and one or two universal workflow constraints.
   - Move specialized guidance into scoped `AGENTS.md` files or linked docs, and update the destination in the same change before deleting the source text.
   - Delete only content that is redundant, non-actionable, obvious boilerplate, or superseded by a resolved contradiction.

5. **Report the outcome**
   - If nothing clears the durable-learning bar, say so and make no changes.
   - Always report learnings, applied updates, and assumptions when needed.
   - If refactoring happened, also report contradictions resolved, deletions, moved guidance, grouped files, and any new folder structure.

## Specific Techniques

### Durable-learning filter

Keep:

- Non-default commands
- Build, test, validation, or typecheck steps
- Repo-specific patterns or constraints
- Environment/configuration quirks
- Warnings and gotchas
- Repeated human corrections

Skip:

- Temporary debugging notes
- Facts obvious from the tree or README
- Navigation/process heuristics inferred from one run unless the user wants them as standing policy
- Generic reminders like "be careful"

### Artifact mining

- Treat prior work artifacts as high-signal source material, not just status metadata.
- Keep durable rules that explain future implementation or test behavior, such as framework constraints, validation rules, stable fix shapes, UX-preservation rules, anti-flake testing tactics, and environment/setup requirements.
- Translate task-specific wording into reusable instructions; keep the lesson, drop ticket names and transient path noise.
- If an existing AGENTS rule captured only one obvious learning while the artifact contains several durable ones, treat that as incomplete and keep mining.

### Placement

- `./AGENTS.md` - near-universal project rules
- `./**/AGENTS.md` - directory/module rules
- Linked docs - longer topic detail referenced from `AGENTS.md`

### Refactor floor

Keep root `AGENTS.md` minimal and safe to always load. Prefer linking over repeating. Never remove guidance unless it is low-value or moved to its new destination in the same change.

## Common Rationalizations

| Rationalization | Reality |
| --- | --- |
| "The root file is enough." | Scoped files or linked docs may own the rule better. |
| "That command is obvious." | Non-default commands are often high-value. |
| "The user didn't ask me to remember this." | Capture durable guidance when warranted. |
| "Only the obvious summary section matters; detailed learnings are too specific." | Durable rules often live in gotchas and useful context, not just the header summary. |
| "Leaving redundant rules is harmless." | Redundancy causes drift. |
| "I moved it, so deleting the old text is enough." | Verify the destination was updated in the same change. |
| "I should update something anyway." | Do not force low-value changes. |

## Red Flags

- Missing, empty, or overly long root `AGENTS.md`
- Mixed global and scoped guidance
- Duplicate or conflicting rules
- Missing, stale, or orphaned linked docs
- Vague or non-actionable rules
- Durable learnings not captured
- A prior work artifact was read but its durable learnings were not preserved
- One-offs added as standing instructions
- Guidance removed from one file without appearing in its destination

## Verification

- [ ] All relevant `AGENTS.md` files were found
- [ ] Directly linked docs were reviewed
- [ ] Durable learnings were placed in the right files
- [ ] One-off and low-value items were excluded
- [ ] Assumptions were stated when needed
- [ ] Root `AGENTS.md` remains minimal
- [ ] Scoped guidance is in the right file
- [ ] Session-note or work-artifact learnings were mined beyond the obvious summary bullets
- [ ] Every moved rule was added to its destination doc in the same change
- [ ] Deletions were applied only where appropriate
- [ ] Duplicate rules were removed or justified
- [ ] Conflicts were surfaced and resolved
- [ ] No orphan links remain
- [ ] Structural changes were explained clearly
<shellId: 0 completed with exit code 0>
```

</details>


---

<sub>⏱️ 10s</sub>

### ✅ `bash`

**Copy fixture repo**

$ rtk mkdir -p outputs/repo
rtk cp -r /home/adam/dev/personal/skills/skills/self-improve/evals/files/noop-fixture/* outputs/repo/
rtk cp -r /home/adam/dev/personal/skills/skills/self-improve/evals/files/noop-fixture/.??* outputs/repo/ 2>/dev/null || true


```

<shellId: 1 completed with exit code 0>
```


---

<sub>⏱️ 13s</sub>

### ✅ `bash`

**Read session notes**

$ rtk read outputs/repo/session_notes.md

<details>
<summary>5 lines</summary>

```
# Session notes

- The agent opened `README.md`.
- One local branch had a temporary name.
- A test run took longer than expected once.
<shellId: 2 completed with exit code 0>
```

</details>


---

<sub>⏱️ 19s</sub>

### ✅ `bash`

**Check repo files**

$ rtk ls -la outputs/repo/

```
644  AGENTS.md  104B
644  README.md  15B
644  session_notes.md  135B
<shellId: 3 completed with exit code 0>
```


---

<sub>⏱️ 24s</sub>

### ✅ `bash`

**Read AGENTS.md**

$ rtk cat outputs/repo/AGENTS.md

```
# AGENTS.md

- Use `python3` for repo scripts.
- Run `pytest tests/unit -q` for unit-test-only changes.
<shellId: 4 completed with exit code 0>
```


---

<sub>⏱️ 28s</sub>

### ✅ `create`

**create a new file at /home/adam/dev/personal/skills/skills/self-improve-workspace/iteration-22/eval-3-noop/old_skill/run-1/outputs/report.md.**

/home/adam/dev/personal/skills/skills/self-improve-workspace/iteration-22/eval-3-noop/old_skill/run-1/outputs/report.md

```
Created file /home/adam/dev/personal/skills/skills/self-improve-workspace/iteration-22/eval-3-noop/old_skill/run-1/outputs/report.md with 503 characters
```


---

<sub>⏱️ 34s</sub>

### 💬 Copilot

I have evaluated the session notes in the benchmark fixture. None qualified as durable guidance, as they were all transient notes or process noise ("opened README.md", "branch had a temporary name", "test run took longer than expected once"). 

No changes were made to `AGENTS.md`. The benchmark repo has been copied to `outputs/repo/` unchanged, and the requested report detailing the outcome was written to `outputs/report.md`.

---

<sub>Generated by [GitHub Copilot CLI](https://github.com/features/copilot/cli)</sub>
