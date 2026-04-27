---
name: prd-to-tasks
description: Break a PRD, plan, feature description, problem statement, or body of work into independently-grabbable GitHub issues using vertical tracer-bullet slices. Use this whenever the user wants to decompose requirements into GitHub issues, child issues, a task tracker issue, AFK/HITL implementation slices, or an issue graph from a PRD or plan, even if they do not explicitly say "prd-to-tasks".
---

# PRD to Tasks

Break a PRD, plan, feature/problem description, or body of work into independently-grabbable GitHub issues. Each issue should be a thin vertical tracer bullet that can be implemented, reviewed, and verified on its own.

Do not implement code while using this skill. The deliverable is a GitHub issue graph: one parent tracker issue plus child implementation issues, or child issues attached to an existing parent issue.

## Inputs

Work from whatever context is already available in the conversation. The user may provide:

- A GitHub issue number or URL containing the source PRD/plan.
- Raw PRD, plan, spec, or feature text.
- A short problem description that needs to become a task graph.
- A target repository, labels, milestone, or project metadata.

If the source material is empty or too vague to identify the intended outcome, ask for the missing PRD, plan, or feature/problem description before creating issues.

## Operating principles

- Slice vertically, not horizontally. A good child issue cuts through the layers needed for one narrow behavior, such as schema, API, UI, tests, and docs where applicable.
- Prefer many thin slices over a few broad issues. Agents can grab small, self-contained work reliably.
- Prefer **AFK** slices over **HITL** slices when reasonable. Mark a slice HITL only when human interaction is genuinely required, such as an architectural decision, design review, security/privacy signoff, or product trade-off.
- Keep issue bodies implementation-guiding without over-prescribing internals. Include likely files, verification, and dependencies, but do not turn the issue into a step-by-step coding transcript.
- Create blockers before blocked issues so later issue bodies can reference real blocker issue numbers.
- Do not close, rename, reword, relabel, or otherwise edit an existing parent issue. Attaching subissues is the intended tracker operation; avoid other parent modifications.

## Workflow

### 1. Gather context

Use context already present in the conversation first.

If the user passes a GitHub issue number or URL, fetch the issue with comments before slicing:

```bash
gh issue view <issue-number-or-url> --comments
```

When a repository is provided or the current repository is ambiguous, pass the repo explicitly:

```bash
gh issue view <issue-number-or-url> --repo <owner/repo> --comments
```

If the issue cannot be fetched because of authentication, permissions, or repository ambiguity, stop and report the exact `gh` failure plus the next action needed.

### 2. Explore the codebase when useful

If you have not already explored the codebase and the source material depends on existing architecture, launch several parallel `code-explorer` subagents. Use distinct lenses so their findings are complementary:

1. Similar user flows and product surfaces.
2. Architecture boundaries, data flow, and extension points.
3. Persistence, API contracts, integrations, and migrations.
4. Tests, accessibility, security, performance, or operational constraints.

Use this prompt shape for each explorer:

```text
We are breaking a PRD/plan into independently-grabbable GitHub issues, not implementing code.

Source material:
<paste the PRD, plan, issue summary, or feature/problem description>

Explore the repository for patterns relevant to <lens>.

Return:
1. Key findings that affect issue boundaries, dependencies, or verification.
2. Existing conventions to preserve.
3. 5-10 likely files or directories with a one-sentence reason for each.
4. Relevant tests or test patterns.
5. Risks, unknowns, or decisions that may require HITL slices.

Do not modify files.
```

If the request is simple or the codebase has already been explored in the current conversation, reuse existing context instead of launching redundant subagents.

### 3. Draft vertical tracer-bullet slices

Break the work into child issues. Each slice should deliver a narrow but complete behavior through every required integration layer.

Vertical-slice rules:

- Each slice delivers one complete path through relevant layers such as schema, API, UI, tests, docs, or operations.
- A completed slice is independently demoable, testable, or otherwise verifiable.
- Avoid horizontal issues like "add database schema", "build all API endpoints", or "create UI components" unless the source work is truly infrastructure-only.
- Keep acceptance criteria to three bullets or fewer. If you need more, split the issue.
- Avoid "and" in issue titles; it usually signals two slices.

Classify each slice:

- **AFK**: Can be implemented and merged without human interaction once assigned.
- **HITL**: Requires human input before or during implementation, such as a product decision, architecture review, design review, compliance/security signoff, or external credential/access setup.

Use dependencies only when one slice truly cannot start until another lands. Do not over-serialize independent work.

### 4. Review the proposed breakdown with the user when required

If the source context came from an existing GitHub issue, present the proposed breakdown before creating child issues. Use a numbered list with this shape:

```markdown
1. **Title**: <short descriptive title>
   **Type**: AFK | HITL
   **Blocked by**: None | Slice <n>: <title>
   **User stories covered**: <story IDs or "Not explicit in source">
```

Ask the user to confirm:

- Does the granularity feel right: too coarse, too fine, or about right?
- Are dependency relationships correct?
- Should any slices be merged or split further?
- Are the correct slices marked HITL and AFK?

Iterate until the user approves the breakdown. If the user provided raw PRD/plan text rather than an existing GitHub issue, use judgment: create issues directly when the breakdown is straightforward, or ask for review when dependencies, scope, or HITL classification are uncertain.

### 5. Prepare the parent tracker issue

If the source was a GitHub issue, treat that issue as the parent tracker. Do not edit its body, title, labels, state, or other metadata.

If the source was not a GitHub issue, create a new parent tracker issue first with a concise title and a body that summarizes the source material and lists the intended child slices. This parent issue exists so agents can determine which task to grab next.

Suggested parent body:

```markdown
## Source

<Short summary of the PRD, plan, feature, or problem description.>

## Task graph

- [ ] <child title or placeholder until created> - AFK/HITL - blocked by <none/title>

## How to grab work

Start with any unchecked AFK issue marked "None - can start immediately" in its Blocked by section. HITL issues require the named human decision or review before implementation.
```

Create the parent with `gh issue create` unless the user explicitly asked for a draft only.

### 6. Create child GitHub issues

Create child issues in dependency order with `gh issue create`: blockers first, then issues they unblock. This lets later issue bodies reference real issue numbers.

Use this issue body template:

```markdown
## Parent

#<parent-issue-number>

## What to build

<A concise description of this vertical slice. Describe the end-to-end behavior, not layer-by-layer implementation chores.>

## Type

AFK | HITL

## Acceptance criteria

- [ ] <Specific, testable condition>
- [ ] <Specific, testable condition>
- [ ] <Specific, testable condition>

## Verification

- [ ] Tests pass: `<targeted test command>`
- [ ] Build succeeds: `<build command, if known>`
- [ ] Manual check: <description of what to verify>

## Blocked by

None - can start immediately
```

Or, when blocked:

```markdown
## Blocked by

- Blocked by #<issue-number>
```

Then continue the body:

```markdown
## User stories covered

<Story IDs/titles from source material, or "Not explicit in source">

## Files likely touched

- `src/path/to/file.ts`
- `tests/path/to/test.ts`

## Estimated scope

Small: 1-2 files | Medium: 3-5 files | Large: 5+ files
```

Omit the Parent section only if there is genuinely no parent tracker, which should be rare.

Create each child issue non-interactively. Prefer writing the body to a temporary file first so shell quoting does not damage Markdown checkboxes or code spans:

```bash
gh issue create --title "<child issue title>" --body-file <body-file>
```

### 7. Attach child issues to the parent

After creating each child issue, attach it to the parent issue using GitHub's subissue GraphQL mutation.

Keep the shell snippet Copilot-safe by inlining the resolved IDs in the GraphQL query text. Do not use GraphQL variables such as `mutation($parentId: ID!, ...)` inside the shell command because `$...` tokens may be blocked as suspicious shell expansion.

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

If attaching subissues fails because the repository or account lacks subissue support, do not delete created issues. Report the child issue numbers and the exact failure, then explain that the parent tracker can still link them manually.

## Task sizing guidelines

| Size | Files | Scope | Example |
|------|-------|-------|---------|
| **XS** | 1 | Single function or config change | Add a validation rule |
| **S** | 1-2 | One component or endpoint | Add a new API endpoint |
| **M** | 3-5 | One feature slice | User registration flow |
| **L** | 5-8 | Multi-component feature | Search with filtering and pagination |
| **XL** | 8+ | Too large - break it down further | N/A |

If a slice is L or larger, split it into smaller vertical slices. Agents perform best on S and M issues.

Break a slice down further when:

- It would take more than one focused implementation session.
- You cannot describe acceptance criteria in three or fewer bullets.
- It touches two or more independent subsystems that can be verified separately.
- The title contains "and".

## Final response

After creating issues, return a concise summary:

```markdown
Created task graph for <feature/source>.

Parent: #<number> <title>

Child issues:
1. #<number> <title> - AFK/HITL - blocked by <none/#n>
2. #<number> <title> - AFK/HITL - blocked by <none/#n>

Notes:
- <Any HITL decisions, attach failures, or assumptions>
```

If the run stopped before creating issues, clearly say whether it stopped during context gathering, review, parent creation, child issue creation, or subissue attachment.

## Quality gate

Before creating child issues, verify:

- Every child issue is a vertical slice, not a horizontal layer.
- Every AFK issue has enough context for an agent to implement without human interaction.
- Every HITL issue names the human decision or review required.
- Dependencies are minimal and accurate.
- Blockers are created before blocked issues.
- Each issue has acceptance criteria, verification, likely files, and scope estimate.
- The parent tracker exists or will be created first.
