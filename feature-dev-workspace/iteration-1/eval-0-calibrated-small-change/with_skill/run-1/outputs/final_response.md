Understanding

I inspected [skills/feature-dev/SKILL.md](skills/feature-dev/SKILL.md). The main issue is not the headline intent; it already says medium-to-large feature work. The problem is that several body sections still expand the scope back down to small changes. I would tighten those sections so the skill only triggers for medium-to-large feature work, and I would shorten the existing "When Not To Use This Skill" section so it reinforces that boundary.

Relevant Findings

The current frontmatter description is partly correct, but still too broad because it says to use the skill whenever the user wants to add a feature, extend a subsystem, or coordinate discovery/design/implementation. That can still trigger on relatively small changes.

The bigger mismatch is in the body:

- Light Track currently says it is for small, well-specified feature work or skill/documentation changes.
- Phase 1 says Light is for small, well-specified work.
- Core Principles says small, well-specified changes should stay lightweight.
- The skill already includes a When Not To Use This Skill section, so I would not add a brand-new section from scratch. I would replace that section with a shorter, sharper version.

Recommendation

I would make four targeted edits.

1. Tighten the frontmatter description.

I would replace the current description with this:

```yaml
description: Structured feature development for medium-to-large feature work in unfamiliar codebases. Use this when the request spans multiple files or subsystems, needs meaningful codebase exploration, or requires design trade-offs, implementation sequencing, and review. Do not use it for small self-contained edits, wording-only skill or documentation changes, tiny bug fixes, or fully specified requests that are ready for direct implementation.
```

Why: this keeps the trigger centered on feature work with real coordination cost, and explicitly excludes the small-change cases that this eval is targeting.

2. Re-scope the workflow language so "light" means smallest in-scope feature work, not genuinely small work.

In Core Principles, I would change this idea:

- Current intent: small, well-specified changes should stay lightweight
- New intent: within in-scope feature work, use the lightest process that matches the risk

Suggested replacement:

```md
- **Calibrate the workflow**: Choose a light, standard, or deep process based on scope, ambiguity, and risk. Even within medium-to-large feature work, some requests are bounded and can stay lightweight, while cross-cutting or unclear features deserve a deeper process.
```

Why: this preserves the calibration concept without implying the skill should trigger for small changes.

3. Rewrite Light Track and the matching Phase 1 bullets.

I would replace the Light Track intro with:

```md
### Light Track

Use for the smallest in-scope feature work: well-bounded medium-sized changes where the main risk is understanding local code context rather than resolving product ambiguity.

- Do focused exploration yourself or with one targeted agent.
- Ask questions only if something is genuinely blocking.
- Give one recommended approach rather than manufacturing multiple options.
- Implement once you have enough context.
```

And in Phase 1, I would change the process selection bullets to:

```md
2. Identify the likely process track:
   - Light for well-bounded medium-sized feature work
   - Standard for broader feature work that touches several files or needs a non-trivial design choice
   - Deep for large, risky, cross-cutting, or highly ambiguous work
```

Why: this is the most important body change. Right now the skill explicitly claims small work and skill/doc changes; removing that language is what actually tightens trigger behavior.

4. Replace the existing When Not To Use This Skill section with a shorter version.

I would use:

```md
## When Not To Use This Skill

Do not use this skill for:

1. Small wording, prompt, skill, or documentation edits
2. Tiny bug fixes or isolated one-file changes
3. Fully specified requests that are ready for direct implementation
4. Pure code review or brainstorming requests with no feature delivery component
```

Why: the section already exists, so the right move is to shorten and sharpen it. This version directly names the exact classes of work that should bypass the skill.

Implementation Map

If I were editing the skill, I would make the changes in this order:

1. Update the frontmatter description so the trigger text is correct first.
2. Update Core Principles and Light Track so the body no longer contradicts the description.
3. Update the Phase 1 process-selection bullets to match the new scope.
4. Replace the existing When Not To Use This Skill section with the shorter version above.
5. Do a final pass for any remaining references to small, straightforward, or documentation-only work so the skill stays internally consistent.

I do not have blocking questions for this task. The current file provides enough context to make the change cleanly and precisely.
