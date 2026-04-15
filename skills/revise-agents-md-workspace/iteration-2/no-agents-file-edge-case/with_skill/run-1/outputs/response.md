## Findings

Since no AGENTS.md exists yet, here are 3 durable learnings worth capturing for future work in this skills repository:

1. **Skills follow a consistent structure**: each skill folder contains `SKILL.md` (with YAML frontmatter), optional `evals/` for testing, and sometimes `references/` or `agents/` subdirectories
2. **Skill descriptions should be specific and tight**: they drive invocation accuracy and appear in tool selection—vague descriptions reduce usefulness
3. **Iteration workspaces are snapshots for skill evals**: folders like `skill-snapshot/` within workspace iterations capture the skill state at eval time, helping track performance across versions

## Proposed updates

### Create: `./AGENTS.md`

Why this file: New AGENTS.md will establish baseline conventions for working with the skills repo, visible to all future sessions.

```markdown
# AGENTS.md — Skills Repository

## Skill Structure
- Each skill lives in `skills/<skill-name>/` with `SKILL.md` at the root
- SKILL.md uses YAML frontmatter: `name`, `description` (drives invocation), and markdown body
- Most skills include `evals/` for test cases and iteration workspaces for development snapshots

## Skill Descriptions Matter
- Descriptions are included in agent context and affect invocation accuracy
- Keep descriptions specific, actionable, and under 1 line when possible
- Use domain keywords that signal when the skill applies

## Evaluation & Iteration
- Eval workspaces (e.g., `iteration-1/`, `skill-snapshot/`) capture skill state during testing
- Use these to track performance changes and debug skill behavior
- Snapshots help correlate eval results to specific skill versions
```

---

**Should I create `./AGENTS.md` with this content?**
