# Update without losing policy

Use before changing existing guidance, including files that will become reference docs.

## Map requirements before edits

For every existing behavioral requirement, identify its scope, trigger, exceptions, evidence, and destination. This can be a compact working list; do not install a migration ledger in the target repository. Assign one disposition:

- **Retain:** still correct at its current scope.
- **Move:** still correct but belongs in a nested guide or conditional reference; preserve its conditions and add a direct route.
- **Merge:** duplicate requirements have the same meaning and scope; retain one authoritative statement.
- **Correct:** current evidence proves a factual detail stale, such as a renamed script; repair the detail without changing policy.
- **Remove:** evidence establishes that the content is obsolete, redundant, or irrelevant. Explain material removals in the final report.
- **Unresolved:** the requirement conflicts with another policy and authority does not settle it; ask a focused question and leave that policy unchanged.

Conciseness is not permission to remove a valid rule. An unusual workflow or stricter test requirement may be deliberate. Missing tooling does not itself revoke a policy; report the mismatch. Conversely, preserve meaning rather than stale wording or a bloated section structure.

## Resolve conflicts from authority and evidence

Apply explicit user decisions and applicable instruction precedence first. Check whether different rules concern different scopes, conditions, or intentional exceptions before labeling them contradictory. Evidence of an existing command can settle a spelling or path correction; it cannot decide an architectural tradeoff or permission policy.

When a policy choice remains, present the conflicting requirements, consequences, and a recommendation. Ask only for that choice. Do not silently select the newest-looking text or treat cited articles as project authority. Keep unrelated authorized edits moving.

## Reconcile references and repeat safely

Read the destination before moving content into it. Preserve human-authored material and existing canonical ownership. Update in-scope incoming links and keep relative paths correct. Delete an obsolete documentation file only when its useful content has a verified destination and its in-scope consumers have been updated; do not remove unrelated documents.

If excluded compatibility files depend on a reference being moved, preserve a working target or report that the full migration needs separately authorized work. Do not follow a symlink edit into an excluded file or outside the target project. Preserve symlinks and report shared-file conflicts instead of replacing them.

Review the resulting diff against the requirement map. Run the task traces and checks in SKILL.md. On a repeated invocation with unchanged evidence, keep adequate content and filenames stable rather than rewriting for style alone.
