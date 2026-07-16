---
name: self-improve
description: Preserves durable repo-specific guidance by updating the right `AGENTS.md` or linked docs, and repairs instruction structure when scope, duplication, conflicts, or drift are wrong. Use whenever the user asks to update/refactor `AGENTS.md`, remember lessons, self improve, preserve human corrections, mine session notes, handoffs, or progress files, or make future agents follow non-default commands, validation steps, gotchas, or linked-doc structure even if they never mention `AGENTS.md`.
---

# Self Improve

Use `SELF_IMPROVE_REFERENCE.md` for examples, judgment calls, rationalizations, and failure modes.

## Overview

Capture durable, reusable learnings in the right `AGENTS.md` or linked doc. Prefer small, precise edits over broad rewrites.

## When to Use

- The user asks to update or refactor `AGENTS.md`, preserve lessons learned, or make future agents remember a workflow or correction.
- Session notes, handoff artifacts, progress files, or similar work records contain reusable commands, validation steps, patterns, quirks, warnings, or human corrections.
- Current instruction files are duplicated, conflicting, stale, poorly scoped, or too bulky to keep prompt-light.
- Not for one-off notes, obvious facts, speculative advice, or transient debugging noise.

## Workflow

1. **Qualify learnings**
   - Keep only items likely to recur, actionable for a future agent, repo/workflow/user-specific, and not already documented.
   - Look for non-default commands, validation/build/typecheck steps, code patterns, environment quirks, warnings, gotchas, repeated human corrections, and recurring agent/harness failure patterns.
   - Mine session notes, handoffs, progress files, and similar artifacts beyond the summary when the details carry durable guidance.
   - Never turn excluded noise into an inverse standing rule.

2. **Map the instruction surface**
   - Activate or load the `subagent-model-router` skill and spawn a fast-tier finder subagent to find every `AGENTS.md`:

   ```bash
   find . -name "AGENTS.md" 2>/dev/null | head -20
   ```

   - Read each one plus any directly linked docs.
   - If no `AGENTS.md` exists, say so and create `./AGENTS.md` with only the strongest 3-7 learnings.

3. **Apply the smallest correct update**
   - Put project-wide rules in `./AGENTS.md`, scoped rules in the nearest existing owning `./**/AGENTS.md`, and longer topic detail in linked docs.
   - Keep prompt-loaded files brief. Prefer one concept per line and exact, actionable wording.
   - Use `<command or pattern>` - `<brief description>` when that makes the rule easier to scan.
   - If root already routes a topic to a linked doc, update that doc instead of splitting related rules across root or new nested `AGENTS.md` files unless the task clearly requires re-scoping.

4. **Refactor only when warranted**
   - Do it when root `AGENTS.md` is over ~120 lines, scope is mixed, rules duplicate or conflict, linked docs are stale or orphaned, or the user asked for cleanup.
   - Resolve contradictions first.
   - Keep root limited to near-universal guidance: short project description, non-default package manager, non-standard build/test/typecheck commands, and one or two universal workflow constraints.
   - Move specialized guidance into scoped `AGENTS.md` files or linked docs. Update the destination in the same change before deleting source text.
   - Delete only content that is redundant, non-actionable, obvious boilerplate, or superseded by a resolved contradiction.

5. **Report the outcome**
   - If nothing clears the durable-learning bar, say so and make no changes.
   - Always report learnings, applied updates, and assumptions when needed.
   - If refactoring happened, also report contradictions resolved, deletions, moved guidance, grouped files, and any new folder structure.

## Specific Techniques

### Durable-learning bar

Keep items that are recurring, actionable, repo/workflow/user-specific, and not already documented. High-value examples: non-default commands, validation/build/typecheck steps, repo-specific constraints, environment quirks, warnings, gotchas, and repeated human corrections.

Skip temporary debugging notes, obvious tree/README facts, one-run navigation heuristics, and generic reminders.

Also qualify agent/harness learnings when artifacts show a concrete prevention rule, narrower validation choice, or instruction cleanup that would likely save future work:

- **Failures:** repeated failed commands, wrong paths, missing dependencies, timeouts, permission issues, retries without new information, and unclear hook errors.
- **Excessive file reading:** repeated reads, full large-file reads, broad scans, always-read docs, and long linked docs loaded for simple tasks.
- **Excessive tool calls:** repeated `ls`/`find`/`grep`, repeated full test runs, polling background work, and planning/search loops without progress.
- **Token waste:** large always-loaded instructions, duplicated skill/doc guidance, verbose required formats, long examples, and copied logs in final answers.
- **Accuracy problems:** contradictory instructions, stale docs, missing definitions of done, paths that do not match the repo, and over-certain claims not grounded in evidence.
- **Execution-time problems:** expensive hooks, full builds where targeted checks would work, repeated dependency installs, avoidable timeouts, and missing cache guidance.
- **Hook problems:** noisy output, unclear failures, unavailable tools, expensive checks on common events, and hooks that block safe workflows.

### Artifact mining

- Treat session notes, handoffs, and progress files as high-signal source material, not just status metadata.
- Preserve reusable rules from patterns, gotchas, and useful context; drop ticket names, temporary blockers, and path noise.
- Do not stop at summary bullets when the detailed sections explain future coding, testing, validation, or environment behavior.
- When one artifact contains several durable learnings, keep representative coverage across them instead of stopping after the first few.
- Keep concrete technical terms when they carry the rule more exactly (`shareReplay(1)`, `aria-describedby`, `nested \`it\``, `single-rule`) instead of paraphrasing them away.
- If the source phrase is itself the durable rule, keep that wording; `nested \`it\`` is stronger than a looser paraphrase like "keep test blocks at describe root."
- Do not discard an artifact-local test or accessibility rule as "too generic" when it is required to preserve that workflow.

### Placement

- `./AGENTS.md` - near-universal project rules
- `./**/AGENTS.md` - directory or module rules
- Linked docs - longer topic detail referenced from `AGENTS.md`

Keep root minimal and safe to always load. Prefer linking over repeating.
Prefer the existing owning scope over inventing a deeper one unless the deeper scope already exists or clearly prevents mixed guidance.
If `api/AGENTS.md` can own API schema validation cleanly, prefer it over creating `api/schema/AGENTS.md` just because the path is narrower.
If one topic doc already owns a workflow, keep related test, accessibility, or state-management learnings with that topic unless they clearly stand alone as repo-wide rules.
Example: if an auth/login progress file says Jasmine forbids `nested \`it\``, keep that exact rule in `docs/auth.md` when that doc already owns the auth workflow.

## Common Rationalizations

| Rationalization                                                                            | Reality                                                                                       |
| ------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------- |
| "Root file is enough" or "broader wording is safer."                                       | Scoped files or linked docs often own the rule better, and specific wording is more useful.   |
| "That command is obvious" or "user didn't ask me to remember this."                        | Non-default commands and repeated corrections are often the highest-value durable guidance.   |
| "Only the summary matters; detailed artifact notes are too specific."                      | Durable rules often live in gotchas and useful context, not only the header summary.          |
| "Leaving redundant rules is harmless" or "I moved it, so deleting the old text is enough." | Redundancy drifts; update the destination in the same change before deleting the source text. |
| "I should update something anyway."                                                        | Do not force low-value changes.                                                               |

## Red Flags

- Mixed global and scoped guidance
- Duplicate or conflicting rules
- Missing, stale, or orphaned linked docs
- Vague or non-actionable rules
- Durable learnings from work artifacts not captured
- One-offs added as standing instructions
- Guidance removed from one file without appearing in its destination

## Verification

- [ ] All relevant `AGENTS.md` files were found
- [ ] Directly linked docs were reviewed
- [ ] Durable learnings were mined beyond obvious summary bullets when needed
- [ ] Durable learnings were placed in the right files
- [ ] One-off and low-value items were excluded
- [ ] Assumptions were stated when needed
- [ ] Root `AGENTS.md` remains minimal
- [ ] Scoped guidance is in the right file
- [ ] Every moved rule was added to its destination doc in the same change
- [ ] Duplicate rules were removed or justified
- [ ] Conflicts were surfaced and resolved
- [ ] No orphan links remain
- [ ] Structural changes were explained clearly
