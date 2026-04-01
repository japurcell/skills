# Feature-Dev: Handoff for Stricter Handoff-Policy Enforcement

## Understanding

**Track selected: Standard.** The request is to produce a handoff artifact—and stop before implementation—for a change that adds stricter enforcement of the handoff-artifact policy inside the feature-dev skill itself. The scope is bounded (one SKILL.md file, three surgical edits), but there is a real design decision: where to insert the enforcement gate and how to avoid conflicting with the existing Light-track optional exception.

---

## Relevant Findings

**`skills/feature-dev/SKILL.md`**

| Location                                                   | Current state                                                                              | Problem                                                                       |
| ---------------------------------------------------------- | ------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------- |
| Default Response Shape, `Artifact Status` entry (line ~65) | "the path to the handoff artifact _when one is created or updated_" — conditional phrasing | Makes creation look optional in all cases                                     |
| Phase 5 Implementation, enforcement aside (line ~147)      | "If you are not implementing yet, produce or update the handoff artifact before stopping"  | Correct intent, but buried as an inline aside inside the implementation phase |
| "When It Is Required" (lines ~191–209)                     | Four conditions, permissive language                                                       | No hard stopping rule; no explicit "workflow violation" consequence           |
| "Quality Bar" (lines ~215–221)                             | Five self-checks, all about artifact content                                               | Does not check whether the file actually exists                               |

**No changes needed** to `references/handoff-plan-template.md` or any agent subdocument.

---

## Open Questions

None — the task is fully specified. Assumptions stated:

- Light-track same-turn completions stay optional (by design, left untouched).
- "Stopping before implementation" = any response that does not include implementation code changes.

---

## Recommendation

Insert a single **PRE-STOP GATE** block immediately after the "When It Is Required" conditions, tighten the `Artifact Status` entry in Default Response Shape to say "required," and add an artifact-existence check to the Quality Bar. Three edits, all in `SKILL.md`.

**Why not per-phase stop checks at phases 3 and 4**: avoids repeating the same rule twice across the file; a single authoritative gate is easier to follow.

---

## Implementation Map

1. **`Default Response Shape` — `Artifact Status` line**: Change "when one is created or updated" → "**required** when stopping before implementation; include the exact path to `handoff-plan.md`".
2. **After the four "When It Is Required" items**: Insert a `> **PRE-STOP GATE — HANDOFF REQUIRED**` block: before any response that stops without implementation, MUST create or update `handoff-plan.md` and include its path in `Artifact Status`. Omitting it is a workflow violation.
3. **Quality Bar**: Add item 6: "The artifact file physically exists at `.agents/scratchpad/<feature-name>/handoff-plan.md` — not just referenced in prose."

Full edit specifications and the ordered slice breakdown are in the handoff artifact.

---

## Artifact Status

Handoff artifact created at:

```
.agents/scratchpad/handoff-policy-enforcement/handoff-plan.md
```

> Workspace-relative path in this eval run:
> `skills/feature-dev-workspace/iteration-9/eval-2-handoff-artifact-policy-enforcement/with_skill/run-1/outputs/.agents/scratchpad/handoff-policy-enforcement/handoff-plan.md`

The artifact is **ready for implementation**. The next agent can apply the three edits to `skills/feature-dev/SKILL.md` directly from the File-by-File Implementation Map, validate with eval 2, and stop.

---

_Stopping here as requested — no implementation performed._
