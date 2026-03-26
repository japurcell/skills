I inspected the current feature-dev skill in this repo, and the cleanest way to make your requested change is to port two targeted edits from the stronger live version into the older snapshot.

First, I would tighten the trigger in the frontmatter description. The older snapshot in [skills/feature-dev-workspace/skill-snapshot/SKILL.md](skills/feature-dev-workspace/skill-snapshot/SKILL.md#L1) is too broad:

```md
description: Guided feature development with codebase understanding and architecture focus
```

I would replace it with the more selective wording already used in [skills/feature-dev/SKILL.md](skills/feature-dev/SKILL.md#L1):

```md
description: Structured feature development for medium-to-large changes in unfamiliar codebases. Use this whenever the user wants to add a feature, extend an existing subsystem, or coordinate discovery, design, implementation, and review across multiple files or moving parts. Prefer it when the task needs codebase exploration, clarifying questions, architecture trade-offs, or a reusable handoff plan for another agent. Do not use it for tiny bug fixes, isolated one-file edits, or straightforward requests that are already fully specified and ready for direct implementation.
```

That change matters because, in this repo, the description is the primary trigger mechanism. This wording explicitly narrows activation to medium-to-large feature work and excludes the small, direct tasks you want to avoid.

Second, I would add a short `When Not To Use This Skill` section, matching the structure already present in [skills/feature-dev/SKILL.md](skills/feature-dev/SKILL.md#L199), and place it near the end of the skill body before the summary section:

```md
## When Not To Use This Skill

Do not use this skill for:

1. Tiny bug fixes or one-file edits where direct implementation is faster than process
2. Fully specified requests that only need straightforward execution
3. Pure code review requests with no feature development component
4. Open-ended brainstorming that does not need codebase-guided implementation planning
```

I would keep the change narrow unless you also want to retune the workflow itself. One important thing I learned from this repo is that the current live feature-dev skill already goes further than your request: it also calibrates process depth, asks fewer default clarifying questions, and avoids turning every feature request into a fully gated multi-phase workflow. If the goal is only to tighten triggering and add the missing guardrail section, I would copy just the description change and the `When Not To Use This Skill` section, and leave the rest of the older skill body as-is.

Nothing here is blocking, so I would not ask questions before making that edit.
