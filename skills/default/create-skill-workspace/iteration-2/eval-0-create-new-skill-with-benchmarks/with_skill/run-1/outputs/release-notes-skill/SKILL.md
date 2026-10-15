---
name: release-notes-skill
description: Helps agents turn merged pull requests, changelog fragments, and issue summaries into polished release notes with clear highlights, grouped changes, upgrade notes, and follow-ups. Use when the user asks to draft release notes, summarize merged work, group changes for a release, or turn PRs/issues into a changelog, even if the inputs are messy, overlapping, or only partially structured.
---

# Release Notes Skill

## Overview

Turn raw release inputs into publishable markdown release notes that explain what shipped, what needs attention during upgrade, and what still needs follow-up. Favor clear user or operator impact over a pasted list of PR titles.

## When to Use

- Draft release notes from merged pull requests, changelog fragments, issue summaries, or handwritten release bullets.
- Rewrite rough internal notes into a cleaner changelog or release summary.
- Group overlapping merged work into one release draft without duplicate bullets.
- Separate shipped changes from upgrade actions and unresolved follow-ups.
- Not for launch marketing copy, roadmap announcements, or retrospective summaries that are not release notes.

## Workflow

1. **Gather the required inputs**
   - Identify or infer the release label, intended audience, and source material.
   - If any of those are missing, say what is missing before drafting.
   - Use only the provided facts. Do not invent shipped work, dates, impact, or urgency.
2. **Normalize the source material**
   - Pull out shipped changes, upgrade actions, and unresolved follow-ups.
   - Merge overlapping PR, issue, and changelog entries before writing.
   - Translate raw implementation detail into the user or operator outcome when possible.
3. **Write the release notes**
   - Use this exact section order:

```md
# Release Notes: <release label>

## Highlights
- <most important shipped outcome>

## Grouped Changes
### <theme>
- <change and impact>

## Upgrade Notes
- <required action, breaking change, verification item, or "None called out.">

## Follow-Ups
- <known gap, deferred work, or "None.">
```

   - Put only the most important 2-5 shipped items in **Highlights**.
   - Put the remaining shipped work into themed subsections under **Grouped Changes**.
   - Put migrations, renamed settings, removed flags, changed defaults, or manual operator steps into **Upgrade Notes**.
   - Put deferred work, rollout checks, doc gaps, and known limitations into **Follow-Ups** instead of presenting them as shipped.
4. **Verify before sending**
   - Check that every bullet traces back to the inputs.
   - Remove duplicate bullets and repeated PR-title wording.
   - Make sure upgrade actions are not buried in Highlights or Grouped Changes.
   - If the inputs do not support a confident claim, say that plainly instead of guessing.

## Specific Techniques

### Input triage

- The minimum useful inputs are: a release label, audience, and one or more merged-work summaries.
- If the audience is mixed, write for the broadest reader and keep operator-only actions in **Upgrade Notes**.
- If the source material is noisy, dedupe first and only then decide what belongs in Highlights.

### Grouping rules

- Group by reader-facing themes such as Authentication, Reporting, Integrations, Reliability, Operations, or Developer Experience.
- Use as many subsections as the input needs; do not force unrelated work into one bucket.
- A one-item subsection is acceptable when it improves scanability.

### Translation rules

- Rewrite PR titles into outcome language, such as turning "add retry wrapper around webhook sender" into "Webhook deliveries now retry transient failures before surfacing an error."
- Keep product names, API names, flags, settings, and migrations when they matter for the reader.
- Omit PR numbers and issue IDs unless the user explicitly asks to keep them.

### Upgrade and follow-up heuristics

- Treat migrations, renamed settings, removed flags, changed defaults, secret rotation, and required backfills as upgrade notes.
- If no action is required, say `- None called out.` rather than leaving the section blank.
- Use Follow-Ups for unresolved work, rollout monitoring, doc cleanup, or manual checks that happen after release.

## Common Rationalizations

| Rationalization | Reality |
| --- | --- |
| "The PR titles are already readable enough." | Raw titles usually over-index on implementation detail and under-explain impact. Rewrite them into release-note language. |
| "I can skip Upgrade Notes when nothing obviously broke." | Readers still need a clear signal about whether action is required. Say `- None called out.` when appropriate. |
| "More bullets make the release feel bigger." | Duplicate or overlapping bullets make the notes noisy and misleading. Merge them into one stronger entry. |
| "A follow-up is close enough to shipped work." | Release notes should distinguish what shipped from what still needs attention so readers know what is actually available. |

## Red Flags

- The output reads like a pasted list of PR titles or issue summaries.
- Highlights are just the first few source bullets instead of the most important shipped changes.
- Upgrade actions are missing even though the input mentions migrations, renamed settings, changed defaults, or operator steps.
- The same change appears twice with slightly different wording.
- Follow-Ups presents future work as already shipped.

## Verification

After drafting the release notes, confirm:

- [ ] The markdown uses `Highlights`, `Grouped Changes`, `Upgrade Notes`, and `Follow-Ups` in that order.
- [ ] Highlights contain the most important shipped items rather than every change.
- [ ] Grouped Changes is organized by theme rather than by PR number.
- [ ] Upgrade Notes calls out required action, verification, or explicitly says `None called out.`
- [ ] Follow-Ups contains only unresolved or post-release work.
- [ ] No bullet depends on facts that were not present in the inputs.
