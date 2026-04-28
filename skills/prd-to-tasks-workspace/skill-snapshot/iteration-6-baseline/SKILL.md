---
name: prd-to-tasks
description: Break a PRD, plan, feature description, problem statement, or body of work into independently-grabbable GitHub issues using thin vertical slices, explicit execution waves, and ready-task guidance. Use this whenever the user wants to turn requirements into child issues, a tracker issue, AFK/HITL slices, or an issue graph future agents can execute from.
---

# PRD to Tasks

Turn a PRD, plan, or feature description into a GitHub issue graph.

Do not implement code while using this skill. The deliverable is either:

- a new parent tracker issue plus child implementation issues, or
- child implementation issues attached to an existing parent issue.

## Parent-tracker decision

Make this decision before drafting any issues:

- If the source PRD already lives in a GitHub issue, that exact issue is already the parent tracker. Reuse that issue as the parent everywhere in the breakdown, child issue bodies, parent-body update, attachment flow, and final summary.
- If the prompt gives the existing parent issue number explicitly, repeat that exact number in every parent reference. Do not swap it for a fresh tracker number or a generic placeholder.
- In that existing-parent case, **never** create another parent tracker, wrapper tracker, queue-guide issue, or nested meta issue. The only new issues should be the executable child implementation slices.
- Create a new parent tracker only when the source is raw PRD/plan/spec/problem text that does not already live in a GitHub issue.

## Response fidelity

Weak models often try to summarize the task graph instead of drafting executable issues. Do not do that here: future agents need issue-ready output, not a sketch.

- Even in dry-run or draft mode, produce the same structural sections you would use for a real run; placeholders are allowed, but missing sections are not.
- Do not stop after a high-level slice list, checklist, or tracker blurb. Draft the child issues with the full issue-body structure, then draft the parent-body update, then draft the subissue attachment commands.
- For existing-parent requests, keep this order:
  1. `## Proposed vertical-slice breakdown (present first)`
  2. Full child issue drafts using the issue body template
  3. Managed parent-body block using `<!-- prd-to-tasks:start --> ... <!-- prd-to-tasks:end -->`
  4. `addSubIssue` attachment commands
- For raw-PRD/new-parent requests, keep this order:
  1. Parent tracker draft or create command
  2. Full child issue drafts using the issue body template
  3. Subissue attachment commands
  4. Final summary
- Do not replace the managed parent-body block with a looser heading such as `## Parent Issue Tracking Guidance` or `## Execution Guidance`.
- Do not collapse child issues into one-line bullets. Each child needs type, acceptance criteria, verification, blockers, queue position, likely files, and scope.

## Inputs

Use whatever context is already in the conversation. The user may provide:

- a GitHub issue number or URL
- raw PRD, plan, spec, or feature text
- a short problem description that needs a task graph
- repository, label, milestone, or project metadata

If the source is too vague to identify the intended outcome, ask for the missing PRD, plan, or feature description before drafting issues.

If the user wants a draft only, or real issue numbers are unavailable, use placeholders such as `#<parent-issue-number>` and clearly label the output as a draft.

## Core rules

- Slice vertically, not horizontally. Each child issue should deliver one narrow but complete behavior through the layers it needs.
- Prefer many thin slices over a few broad ones.
- Prefer **AFK** unless a human decision, review, approval, or access gate is genuinely required.
- Keep issue bodies implementation-guiding without turning them into coding transcripts.
- Create blockers before blocked issues so later issue bodies can reference real blocker issue numbers.
- Keep existing parent metadata unchanged. You may update its body only by appending or refreshing a dedicated managed task-graph section.
- Make the next ready AFK task obvious from GitHub alone.
- If the source already is a GitHub issue, do not add any extra tracker layer; the executable work must stay as that issue's direct child subissues.

## Workflow

### 1. Gather source context

Reuse conversation context first.

If the user passes a GitHub issue number or URL, fetch the issue with comments before slicing:

```bash
gh issue view <issue-number-or-url> --comments
```

When the repository is ambiguous, pass it explicitly:

```bash
gh issue view <issue-number-or-url> --repo <owner/repo> --comments
```

If the fetch fails because of authentication, permissions, or repository ambiguity, stop and report the exact `gh` failure plus the next action needed.

Use issue comments and follow-up constraints when deciding slice boundaries, dependencies, and ordering.

### 2. Explore the codebase only when it matters

If the source depends on existing architecture and you do not already have enough repository context, launch several parallel `code-explorer` subagents with complementary lenses:

1. Similar product flows and user surfaces.
2. Architecture boundaries, data flow, and extension points.
3. Persistence, API contracts, integrations, and migrations.
4. Tests, accessibility, security, performance, and operational constraints.

Ask each explorer for:

1. Key findings that affect issue boundaries, dependencies, or verification.
2. Existing conventions to preserve.
3. Likely files or directories to mention in issue bodies.
4. Relevant tests or test patterns.
5. Risks, unknowns, or decisions that may require HITL slices.

If the request is simple or the codebase has already been explored in the current conversation, skip this step.

### 3. Draft vertical tracer-bullet slices

Break the work into child issues. Each slice should deliver one independently demoable, testable, or otherwise verifiable behavior.

Rules for slices:

- Avoid horizontal issues like "database schema", "all API endpoints", or "UI components" unless the work is truly infrastructure-only.
- Keep acceptance criteria to three bullets or fewer. If you need more, split the issue.
- Avoid "and" in titles; it often signals two slices.
- Use dependencies only when one slice truly cannot start until another lands.

Classify every slice:

- **AFK**: can be implemented and merged without human interaction once assigned
- **HITL**: requires a human decision, review, approval, or access step before or during implementation

Assign every slice an explicit **execution wave**:

- **W1**: can start immediately once the task graph exists
- **W2+**: must wait for earlier blockers or earlier waves
- reuse the same wave only for AFK slices that can genuinely proceed in parallel once blockers are closed

Future agents need a deterministic rule for what comes next, so do not leave ordering implicit.

Prefer S/M slices. Split a slice if it would take more than one focused implementation session, touch more than roughly 5 files, need more than three acceptance bullets, or span multiple subsystems that can be verified separately.

### 4. Existing-parent requests: present the breakdown first and keep the same parent

If the source came from an existing GitHub issue, start by presenting the proposed breakdown before creating child issues. Use this shape:

```markdown
## Proposed vertical-slice breakdown (present first)

1. **Title**: <short descriptive title>
   **Type**: AFK | HITL
   **Execution wave**: W<n>
   **Blocked by**: None | Slice <n>: <title>
   **User stories covered**: <story IDs or "Not explicit in source">
```

If the user needs approval before any GitHub mutation, stop after the breakdown and ask for it.

After the breakdown, keep drafting against that same parent issue. Do not create a fresh tracker issue just to hold queue guidance; put the managed task-graph guidance on the existing parent body instead.

If the request is a draft or dry run, still draft the full child issue bodies, managed parent-body block, and `addSubIssue` commands. The only difference is that placeholders are acceptable where live issue numbers are unavailable.

If the user asked for a dry run, inline draft, or all-in-one answer, present the breakdown first and then continue with the draft issues in the same response, using placeholders where needed.

If the source is raw PRD or plan text rather than an existing GitHub issue, use judgment: create issues directly when the breakdown is straightforward, or pause for review when scope, dependencies, or HITL classification are uncertain.

### 5. Prepare the parent tracker issue

If the source was a GitHub issue, treat that exact issue as the parent tracker. Keep its title, labels, state, assignees, and unrelated body content untouched.

When the parent already exists, use its body as the durable queue record by appending or refreshing a managed task-graph section after the child issue numbers are known. Replace only the managed block; do not rewrite the whole body. Do not create a second tracker issue for queue guidance, documentation, or nesting.

If the source was not a GitHub issue, create a new parent tracker issue first with a concise title and a body like this:

```markdown
## Source

<Short summary of the PRD, plan, feature, or problem description.>

## Task graph

- [ ] W<n> - <child title or placeholder until created> - AFK/HITL - blocked by <none/title>

## How to grab work

Work is executed from this issue's direct subissues. Start with any open AFK issue in the lowest-numbered wave whose blockers are all closed. If multiple AFK issues share that wave and do not block one another, they may be worked in parallel. HITL issues require the named human decision or review before implementation.
```

Create the parent with `gh issue create` unless the user explicitly asked for a draft only.

### 6. Create child GitHub issues

Create child issues in dependency order with `gh issue create`: blockers first, then the issues they unblock.

Use this issue body template:

```markdown
## Parent

#<parent-issue-number>

## What to build

<Describe the end-to-end behavior of this slice, not layer-by-layer chores.>

## Type

AFK | HITL

## Acceptance criteria

- [ ] <Specific, testable condition>
- [ ] <Specific, testable condition>
- [ ] <Specific, testable condition>

## Verification

- [ ] Tests pass: `<targeted test command>`
- [ ] Build succeeds: `<build command, if known>`
- [ ] Manual check: <what to verify manually>

## Blocked by

None - can start immediately

## Queue position

- Parent queue: direct subissue of #<parent-issue-number>
- Execution wave: W<n>
- Ready to start when: this issue has no blockers, or every issue listed in `Blocked by` is closed

## User stories covered

<Story IDs/titles from source material, or "Not explicit in source">

## Files likely touched

- `src/path/to/file.ts`
- `tests/path/to/test.ts`

## Estimated scope

Small: 1-2 files | Medium: 3-5 files | Large: 5+ files
```

When blocked, replace the `Blocked by` section with:

```markdown
## Blocked by

- Blocked by #<issue-number>
```

Keep the same `Queue position` section for blocked issues, but make the `Ready to start when` line explicitly reference blocker closure.

Create each child issue non-interactively. Prefer a body file so Markdown survives shell quoting:

```bash
gh issue create --title "<child issue title>" --body-file <body-file>
```

### 7. Update an existing parent issue with durable tracking guidance

When the parent tracker already exists as a GitHub issue, update its body after the child issue numbers are known. The parent body should make clear that:

- the executable tasks are the parent issue's direct subissues
- each task belongs to an execution wave
- future agents should pick the lowest ready AFK task next

Use this managed block:

```markdown
<!-- prd-to-tasks:start -->

## Task graph

- [ ] W1 - #<child-issue-number> <title> - AFK/HITL - blocked by <none/#n>
- [ ] W2 - #<child-issue-number> <title> - AFK/HITL - blocked by <none/#n>

## How to grab work

1. Open this parent issue and inspect its direct subissues.
2. The executable work is in the sibling implementation issues listed above.
3. Pick any open AFK issue in the lowest-numbered wave whose blockers are all closed.
4. If several AFK issues are ready in the same wave, they may be worked in parallel.
5. Do not start HITL issues until the named human decision or review has happened.
<!-- prd-to-tasks:end -->
```

Suggested update flow:

```bash
CURRENT_BODY_FILE=$(mktemp)
UPDATED_BODY_FILE=$(mktemp)
gh issue view <parent-issue-number> --json body --jq .body > "$CURRENT_BODY_FILE"
python3 - "$CURRENT_BODY_FILE" "$UPDATED_BODY_FILE" <<'PY'
from pathlib import Path
import re, sys
current = Path(sys.argv[1]).read_text(encoding="utf-8")
managed_block = """<!-- prd-to-tasks:start -->
## Task graph

- [ ] W1 - #<child-issue-number> <title> - AFK/HITL - blocked by <none/#n>
- [ ] W2 - #<child-issue-number> <title> - AFK/HITL - blocked by <none/#n>

## How to grab work

1. Open this parent issue and inspect its direct subissues.
2. The executable work is in the sibling implementation issues listed above.
3. Pick any open AFK issue in the lowest-numbered wave whose blockers are all closed.
4. If several AFK issues are ready in the same wave, they may be worked in parallel.
5. Do not start HITL issues until the named human decision or review has happened.
<!-- prd-to-tasks:end -->"""
pattern = re.compile(r"<!-- prd-to-tasks:start -->.*?<!-- prd-to-tasks:end -->", re.S)
updated = pattern.sub(managed_block, current) if pattern.search(current) else f"{current.rstrip()}\n\n{managed_block}\n"
Path(sys.argv[2]).write_text(updated, encoding="utf-8")
PY
gh issue edit <parent-issue-number> --body-file "$UPDATED_BODY_FILE"
```

### 8. Attach child issues to the parent

After creating each child issue, attach it to the parent issue with `addSubIssue`.

Inline the resolved IDs in the GraphQL query text. Do not use GraphQL variables such as `mutation($parentId: ID!, ...)` inside the shell command.

```bash
PARENT_ISSUE_ID=$(gh issue view <parent-issue-number> --json id --jq .id)
CHILD_ISSUE_ID=$(gh issue view <child-issue-number> --json id --jq .id)
gh api graphql -f query="
mutation {
  addSubIssue(input: {issueId: \"$PARENT_ISSUE_ID\", subIssueId: \"$CHILD_ISSUE_ID\"}) {
    issue { number }
  }
}"
```

If subissue attachment fails because the repository or account lacks support, do not delete created issues. Report the exact failure and explain that the parent tracker can still link the children manually.

## Final response

After creating or drafting the issues, return a concise summary:

```markdown
Created task graph for <feature/source>.

Parent: #<number> <title>

Child issues:

1. #<number> <title> - W<n> - AFK/HITL - blocked by <none/#n>
2. #<number> <title> - W<n> - AFK/HITL - blocked by <none/#n>

How to grab work:

- Open parent #<number> and inspect its direct subissues.
- Pick the lowest-numbered open AFK wave whose blockers are all closed.
- If the parent issue already existed, read the managed `Task graph` / `How to grab work` section in its body.

Notes:

- <Any HITL decisions, attachment failures, or assumptions>
```

If the run stopped early, clearly say whether it stopped during context gathering, review, parent creation, child issue creation, parent-body update, or subissue attachment.

## Final checklist

Before finishing, verify:

- every child issue is a vertical slice, not a horizontal layer
- every AFK issue has enough context for an implementation agent to start without human interaction
- every HITL issue names the human decision or review required
- dependencies are minimal and accurate
- execution waves make the next ready AFK issue obvious from GitHub alone
- blockers are created before blocked issues
- each issue has acceptance criteria, verification, likely files, scope estimate, and queue position
- the parent tracker exists or was drafted first
- if the parent already existed, its managed task-graph block makes the sibling subissue queue explicit without overwriting unrelated content
- if the source already lived in a GitHub issue, no extra parent tracker or wrapper issue was created
