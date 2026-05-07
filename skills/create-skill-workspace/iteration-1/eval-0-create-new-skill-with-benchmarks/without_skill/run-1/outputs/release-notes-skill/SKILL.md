---
name: release-notes-skill
description: Helps agents turn merged pull requests, changelog fragments, and issue summaries into polished release notes with clear highlights, grouped shipped changes, upgrade notes, and follow-ups. Use when the user asks for release notes, a release summary, grouped changelog notes, or wants PRs/issues rewritten into publishable markdown.
---

# Release Notes Skill

## Overview

Turn messy release inputs into publishable markdown that explains what shipped, what readers need to do before or after upgrade, and what work did not ship yet. The goal is a clean release-note draft, not a pasted list of PR titles.

## When to Use

- Draft release notes from merged PRs, changelog fragments, incident summaries, issue digests, or hand-written bullets.
- Clean up rough internal notes into publishable release notes for customers, operators, or internal stakeholders.
- Merge overlapping PR and issue summaries into one deduplicated release draft.
- Call out upgrade actions, changed defaults, migrations, or post-release checks separately from shipped features.
- Not for launch marketing copy, roadmap announcements, or retrospective summaries that are not release notes.

## Workflow

1. **Collect the minimum inputs**
   - Gather the release label, audience, and raw change inputs.
   - If one of those is missing, infer only what is obvious from the provided material and say what remains unknown.
   - Do not invent shipped work, dates, rollout status, or breaking changes.
2. **Sort the source material**
   - Separate shipped outcomes, operator or user actions, and unresolved follow-ups.
   - Merge overlapping PR, issue, and changelog entries before writing.
   - Translate low-level implementation detail into user-facing impact when possible.
3. **Prioritize the draft**
   - Put only the most important shipped changes in **Highlights**.
   - Put the remaining shipped work into themed subsections under **Grouped Changes**.
   - Move migrations, renamed settings, removed flags, changed defaults, or required manual steps into **Upgrade Notes**.
   - Move deferred work, monitoring checks, known gaps, and post-release cleanup into **Follow-Ups**.
4. **Write the markdown in this exact order**

```md
# Release Notes: <release label>

## Highlights
- <most important shipped outcome>

## Grouped Changes
### <theme>
- <shipped change and its impact>

## Upgrade Notes
- <required action, breaking change, verification step, or "None called out.">

## Follow-Ups
- <known gap, deferred work, or "None.">
```

5. **Do a final accuracy pass**
   - Make sure every bullet traces back to the provided inputs.
   - Remove duplicate bullets and repeated PR-title phrasing.
   - Ensure upgrade actions are not buried inside Highlights or Grouped Changes.
   - If the inputs are incomplete, say so plainly instead of filling gaps with guesses.

## Specific Techniques

### Input checklist

- Prefer these inputs in order: release label, audience, merged work items, upgrade risks, known follow-ups.
- If the user gives only PRs or issues, infer themes from the work instead of inventing a taxonomy in advance.
- Keep raw IDs out of the bullets unless the user explicitly asks for them.

### Grouping and rewriting

- Group by reader-facing themes such as Authentication, Reporting, Integrations, Reliability, Operations, or Developer Experience.
- Keep a single-item subsection when it makes the output easier to scan.
- Rewrite terse PR titles into outcomes, such as turning "retry webhook send on timeout" into "Webhook deliveries now retry transient failures before surfacing an error."
- If two inputs describe the same shipped change, keep one bullet and fold the best detail into it.

### Upgrade and follow-up rules

- Treat migrations, renamed settings, secret rotation, removed flags, changed defaults, and manual config steps as upgrade notes.
- If no upgrade action is needed, write `- None called out.`
- If no follow-up remains, write `- None.`
- Never present deferred work or release-monitoring tasks as if they already shipped.

## Common Rationalizations

| Rationalization | Reality |
| --- | --- |
| "The PR titles are already clear enough." | PR titles often expose implementation detail instead of user impact. Rewrite them into release-note language. |
| "More bullets makes the release look bigger." | Duplicate or overlapping bullets make the notes noisy and misleading. Merge related inputs into one stronger point. |
| "If there is no upgrade work, I can leave that section empty." | Readers need an explicit signal that no action is required. Use `- None called out.` |
| "A follow-up is close enough to shipped work." | Release notes must distinguish what shipped from what still needs verification or cleanup. |

## Red Flags

- The output reads like copied PR titles with minimal rewriting.
- Highlights are just the first items from the source list instead of the most important shipped changes.
- Grouped Changes is one unthemed bullet list.
- Upgrade Notes omits a rename, migration, or manual action mentioned in the inputs.
- Follow-Ups describes planned or deferred work as if it already shipped.

## Verification

After drafting the release notes, confirm:

- [ ] The markdown uses `Highlights`, `Grouped Changes`, `Upgrade Notes`, and `Follow-Ups` in that order.
- [ ] Highlights contain only the most important shipped items.
- [ ] Grouped Changes uses reader-facing themes instead of PR-by-PR bullets.
- [ ] Upgrade Notes calls out required action, or explicitly says `None called out.`
- [ ] Follow-Ups contains only unresolved or post-release work, or explicitly says `None.`
- [ ] No bullet depends on facts that were not present in the inputs.
