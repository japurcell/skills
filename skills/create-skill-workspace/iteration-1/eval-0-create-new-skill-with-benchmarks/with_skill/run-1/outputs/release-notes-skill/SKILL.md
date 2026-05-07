---
name: release-notes-skill
description: Helps agents turn merged pull requests, changelog fragments, and issue summaries into polished release notes with clear highlights, grouped changes, upgrade notes, and follow-ups. Use when the user asks for release notes, a changelog draft, a release summary, or wants PRs/issues grouped into publishable notes, even if the inputs are messy or partially duplicated.
---

# Release Notes Skill

## Overview

Turn raw release inputs into concise markdown release notes that explain what shipped, what needs attention during upgrade, and what still needs follow-up. The goal is to produce publishable notes, not a cleaned-up dump of PR titles.

## When to Use

- Draft release notes from merged PRs, changelog fragments, issue summaries, or handwritten release bullets.
- Clean up a rough changelog into publishable notes for customers, operators, or internal users.
- Consolidate overlapping PR and issue summaries into one release draft without duplicate bullets.
- Add upgrade notes or follow-ups when some changes need operator action or are not fully complete.
- Not for marketing launch copy, roadmap announcements, or internal retrospectives that are not release notes.

## Workflow

1. **Gather the frame**
   - Confirm or infer the release label, audience, and input sources.
   - If key context is missing, say what is missing before drafting.
   - Use only the provided facts; do not invent shipped work, dates, or severity.
2. **Normalize the source material**
   - Extract shipped changes, operator actions, and unresolved follow-ups.
   - Merge duplicate PR and issue summaries before writing.
   - Separate implementation detail from user impact so the notes stay readable.
3. **Prioritize the story**
   - Put the 2-5 most important user-visible or operator-visible items in **Highlights**.
   - Put the rest into themed subsections under **Grouped Changes**, not PR-by-PR bullets.
   - Move migrations, renamed settings, removed flags, changed defaults, or manual actions into **Upgrade Notes**.
   - Move known gaps, deferred work, and post-release checks into **Follow-Ups** instead of presenting them as shipped.
4. **Write the markdown output**
   - Use this exact section order:

```md
# Release Notes: <release label>

## Highlights
- <most important shipped outcome>

## Grouped Changes
### <theme>
- <change and impact>

## Upgrade Notes
- <required action, breaking change, or "None called out.">

## Follow-Ups
- <known gap, deferred item, or "None.">
```

   - Keep bullets concrete and brief.
   - Prefer user-facing language over raw implementation detail, but retain product names, APIs, flags, or migrations when they matter.
5. **Verify before sending**
   - Ensure every bullet traces back to the inputs.
   - Remove duplicate bullets and repeated PR-title phrasing.
   - Check that upgrade actions are not buried in Highlights or Grouped Changes.
   - If the source material is incomplete, say so plainly instead of filling gaps with guesswork.

## Specific Techniques

### Grouping rules

- Group by theme such as Authentication, Reporting, Integrations, Reliability, Developer Experience, or Operations.
- Use as many theme subsections as the input needs; do not force everything into one bucket.
- Keep a one-item subsection if it makes the draft easier to scan.

### Translating noisy inputs

- Rewrite raw PR titles into outcome language, such as turning "add retry wrapper around webhook sender" into "Webhook deliveries now retry transient failures before surfacing an error."
- Keep issue IDs and PR numbers out of bullets unless the user explicitly asks for them.
- If multiple inputs describe the same change at different levels of detail, keep the clearest version and fold the best supporting detail into the same bullet.

### Upgrade-note heuristics

- Treat migrations, renamed settings, removed flags, changed defaults, required backfills, and secret rotation as upgrade notes.
- If no action is required, say so with `- None called out.` rather than leaving the section empty.
- If an item is risky but not fully confirmed as breaking, mark it as something to verify before rollout instead of overstating certainty.

### Follow-up heuristics

- Use Follow-Ups for known limitations, deferred cleanup, doc gaps, rollout monitoring, and manual checks after release.
- Do not put planned future work in Grouped Changes as if it already shipped.

## Common Rationalizations

| Rationalization | Reality |
| --- | --- |
| "The PR titles already look readable enough." | Raw titles usually duplicate implementation detail and hide user impact. Translate them into release-note language. |
| "I can leave upgrade notes blank when nothing obvious broke." | Readers still need a clear signal that no action is required. Use `- None called out.` when appropriate. |
| "If two inputs overlap, more bullets makes the release look fuller." | Duplicate bullets make the notes noisy and misleading. Merge overlapping inputs into one stronger bullet. |
| "A follow-up item is close enough to shipped work; I'll include it under changes." | Release notes should distinguish shipped outcomes from remaining work so readers know what is actually available. |

## Red Flags

- The output reads like a pasted list of PR titles or issue summaries.
- Highlights are just the first bullets from the source list instead of the most important changes.
- Upgrade actions are missing even though the inputs mention migrations, default changes, renamed settings, or secret rotation.
- The same change appears in Highlights and Grouped Changes with only wording differences.
- Follow-Ups claims future work already shipped.

## Verification

After drafting the notes, confirm:

- [ ] The markdown uses `Highlights`, `Grouped Changes`, `Upgrade Notes`, and `Follow-Ups` in that order.
- [ ] Highlights contain only the most important shipped items rather than every change.
- [ ] Grouped Changes are organized by theme rather than PR number.
- [ ] Upgrade Notes call out required operator or user action, or explicitly say `None called out.`
- [ ] Follow-Ups contain only unresolved or post-release work.
- [ ] No bullet depends on facts that were not present in the inputs.
