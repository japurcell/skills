# Validation checklist

Before saving `tasks.json`, confirm:

- [ ] Tasks are implementation-sized **vertical slices**.
- [ ] Required prefactoring is independently valuable and verifiable.
- [ ] Every explicit requirement maps to at least one task or acceptance criterion.
- [ ] Edge cases, fallbacks, negative states, and partial failures are covered.
- [ ] Out-of-scope items are excluded.
- [ ] Conflicts are resolved, documented, or escalated.
- [ ] IDs are sequential and unique.
- [ ] Mandatory order is reflected in task order and priority.
- [ ] Priorities are unique and ascending.
- [ ] Top-level `project`, `branchName`, and `description` are present and valid.
- [ ] Each task includes `Typecheck passes`.
- [ ] Exact commands are used only when known.
- [ ] UI-visible tasks include `Verify in browser using playwright-cli skill`.
- [ ] Backend-only tasks avoid UI/browser wording.
- [ ] `filesLikelyTouched` includes inferable source, tests, scripts, configs, migrations, fixtures, and command targets.
- [ ] `passes` is `false` for every task.
- [ ] `notes` is `""` for every task.
- [ ] The output file is valid JSON only, with no markdown, comments, explanations, or trailing commas.
