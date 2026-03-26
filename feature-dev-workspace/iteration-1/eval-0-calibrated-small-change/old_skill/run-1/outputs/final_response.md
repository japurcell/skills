I inspected the current `feature-dev` skill in this repo and compared it with the requested change. The repo already moved in the right direction: the frontmatter description is narrowed toward larger feature work, and there is already a `When Not To Use This Skill` section. The one place that still weakens the intent is the `Light Track`, which explicitly says the skill is for small, well-specified work. If the goal is to make this skill trigger only for medium-to-large feature work, I would tighten that inconsistency rather than only tweaking the summary text.

Here is exactly how I would make the change.

## 1. Tighten the trigger text in frontmatter

I would make the description the primary trigger control and keep it explicit about scope. The current repo version is close to correct. I would use wording in this shape:

```md
---
name: feature-dev
description: Structured feature development for medium-to-large changes in unfamiliar codebases. Use this whenever the user wants to add a feature, extend an existing subsystem, or coordinate discovery, design, implementation, and review across multiple files or moving parts. Do not use it for tiny bug fixes, isolated one-file edits, or straightforward requests that are already fully specified and ready for direct implementation.
argument-hint: Optional feature description
disable-model-invocation: true
---
```

That does two things cleanly:

- It positively names the intended scope: medium-to-large feature work.
- It negatively names the exclusions so small direct-execution tasks do not match as easily.

## 2. Remove or rewrite the `Light Track`

This is the main follow-through change I would make in the body. Right now the live skill still says:

- `Light Track` is for small, well-specified feature work or skill/documentation changes.

That directly conflicts with the requested trigger boundary. I would choose one of these two options:

1. Preferred: remove `Light Track` entirely and keep only `Standard Track` and `Deep Track`.
2. Acceptable: rewrite `Light Track` so it is only for a smaller execution slice inside an already medium-sized feature effort, not for standalone small tasks.

If the goal is strict calibration, I would take option 1. That means updating:

- `Process Selection`
- the Discovery bullets that mention `Light`
- the Exploration bullets that branch on `Light`
- the Architecture Design bullets that branch on `Light`
- the Quality Review bullets that branch on `Light`

The result should say, in effect: use this skill when the work is large enough to justify exploration and design, then choose between a standard-depth and deep-depth process.

## 3. Keep the `When Not To Use This Skill` section short and explicit

The repo already contains this section, and it is the right shape. I would keep it short, like this:

```md
## When Not To Use This Skill

Do not use this skill for:

1. Tiny bug fixes or one-file edits where direct implementation is faster than process
2. Fully specified requests that only need straightforward execution
3. Pure code review requests with no feature development component
4. Open-ended brainstorming that does not need codebase-guided implementation planning
```

That is short enough to act as a routing hint without turning into policy sprawl.

## 4. Make the surrounding guidance consistent with the tighter trigger

I would keep the newer repo wording that reduces unnecessary ceremony, because it supports the same calibration goal:

- prefer `Ask only high-leverage questions` instead of always asking clarifying questions
- avoid artificial approval gates before implementation
- present one recommended approach unless there is a real architectural fork

Those changes are not the headline request, but they help prevent the skill from behaving like a heavyweight workflow on tasks that should never have invoked it in the first place.

## Bottom line

If I were editing this skill, I would treat the change as mostly done already in the current repo and make one additional tightening pass:

1. Keep the narrowed frontmatter description.
2. Keep the short `When Not To Use This Skill` section.
3. Remove or rewrite `Light Track`, because that is the remaining place where the skill still claims small-work scope.

That gives you a skill that is clearly aimed at medium-to-large feature development and is less likely to trigger for small, direct implementation tasks.
