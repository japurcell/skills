# Benchmark Run Output

Recommended save path: `~/.agents/skills/doc-to-sop/SKILL.md`

Invocation command: `/doc-to-sop $source_doc $audience`

Assumptions:

- The confirmed session summary in `/home/adam/.agents/skills/skillify/evals/files/personal-docs-to-sop.md` is treated as the completed interview and source of truth for this benchmark run.
- This workflow should be a personal skill because it is intended to follow the user across repositories.
- The skill should run inline, so no `context` frontmatter field is included.
- Allowed tools were kept narrow to match the observed workflow: `Read`, `Grep`, `Glob`, `Edit`, and `Write`.
- No shell automation, package installation, or extra arguments were added because the confirmed summary explicitly kept the workflow focused on reading, extracting, and writing.
