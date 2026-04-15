Recommended save path: `~/.agents/skills/doc-to-sop/SKILL.md`

Invocation command: `/doc-to-sop $source_doc $audience`

Assumptions:

- The confirmed session summary is authoritative, so no follow-up questions were needed for this benchmark run.
- A standard markdown skill file with frontmatter is an acceptable output format for the personal skill.
- Audience-specific tailoring should be handled through wording and emphasis, not by adding more arguments.
- The generated skill should return the derived `SKILL.md` inline for review before the user saves it.
