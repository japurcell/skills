Recommended save path: `~/.agents/skills/doc-to-sop/SKILL.md`

Invocation command: `/doc-to-sop $source_doc $audience`

Assumptions:

- The confirmed session summary already captures the final user-approved requirements.
- The skill should be reusable across repositories, so the recommended destination is a personal skills directory.
- The workflow should stay focused on reading, extracting, and writing, without adding shell or package-install steps unless the source material explicitly includes them.
- Inline output is acceptable because the user prefers to tweak wording before saving.
