# Document Quality

Give future agents the least context needed to act correctly.

## Write

- Use short headings, bullets, and direct language.
- Update an existing focused doc before creating one.
- Put each fact or rule in one canonical location.
- Link to details instead of repeating them.
- Keep instructions and memory separate.
- Describe current behavior, not how the task unfolded.

## Split

Split a document when it:

- Mixes unrelated topics
- Combines instructions with memory
- Contains narrow details most agents do not need
- Forces agents to scan a large file for one fact
- Combines variants that are usually used separately

Keep tightly coupled variants together. Otherwise, give each provider, runtime, platform, or tool its own focused doc and link to it from an index.

## Deduplicate

When guidance is duplicated:

1. Choose the canonical doc.
2. Merge unique, durable content into it.
3. Delete duplicate text.
4. Add a link only if it improves routing.
5. Update indexes and links.

## Do Not Store

- One-off task notes
- Raw logs or command output
- Debug transcripts
- Temporary workarounds
- Speculation
- What the codebase already shows
- Summaries of previous work

## Final Check

Check touched and related docs for:

- Stale, duplicate, or contradictory guidance
- Content that belongs in a focused doc
- Instructions stored as memory, or memory stored as instructions
- Missing or vague index entries
- Broken links
- Task narratives, logs, or temporary details
- What the codebase already shows
