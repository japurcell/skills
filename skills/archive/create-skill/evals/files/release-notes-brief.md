# Brief: release-notes-skill

Create a skill named `release-notes-skill`.

The skill should help an agent turn merged pull requests, changelog fragments, or issue summaries into polished release notes.

## Behavior

- Use the repository skill anatomy structure.
- Trigger when the user asks to draft release notes, summarize merged work, group changes for a release, or turn PRs/issues into a changelog.
- Produce a predictable markdown output with sections for highlights, grouped changes, upgrade notes, and follow-ups.
- Keep the workflow concise and explain which inputs it needs.

## Quality requirements

- Add realistic eval coverage.
- Ship a deterministic benchmark grader if the outputs can be checked objectively.
- Keep the skill concise enough for weaker models to follow.
- Document the exact validation and install-refresh commands a contributor should run in this repo.
