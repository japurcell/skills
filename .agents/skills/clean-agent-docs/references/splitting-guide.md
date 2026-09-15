# Progressive Disclosure and Document Splitting

Use this guide only when a document mixes topics, audiences, or loading triggers.

## Keep content in the overview when it is

- Needed for most tasks
- Required to route readers correctly
- A short repository-wide rule
- Necessary to avoid a common serious error

## Move content to a focused document when it is

- Relevant only to one subsystem, tool, language, or workflow
- Detailed reference material
- A rare exception or troubleshooting path
- Large enough to distract from common instructions
- Triggered by a condition that can be stated in one line

## Split by trigger

Create separate documents when readers would choose between distinct paths, such as:

- frontend vs. backend
- testing vs. deployment
- local development vs. production operations
- routine work vs. incident response
- general rules vs. tool-specific instructions

Do not split solely to make files shorter. Each new document must have a distinct loading trigger.

## Pointer format

Use a short pointer:

> For `<task or condition>`, read [`<document>`](<path>). Skip it for `<nonmatching condition>`.

Example:

> For database schema changes, read [`database-migrations.md`](database-migrations.md). Skip it for application-only changes.

## Structure rules

- Keep each rule in one canonical document.
- Link directly to focused documents; avoid long pointer chains.
- Keep reference files one directory level below `SKILL.md` when practical.
- Give files descriptive names based on their trigger.
- Update all affected indexes and inbound links after moving content.
- Remove obsolete source text after verifying the new destination.
