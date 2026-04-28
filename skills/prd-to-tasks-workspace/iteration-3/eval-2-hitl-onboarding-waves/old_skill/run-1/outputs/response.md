Created task graph for workspace onboarding that guides a new admin through inviting teammates, connecting Slack, and completing the first project setup.

Parent: #<parent-issue-number> Workspace onboarding for new admins

Child issues:
1. #<child-1-issue-number> Review workspace onboarding UI before implementation - HITL - blocked by none
2. #<child-2-issue-number> Add teammate invite step to workspace onboarding - AFK - blocked by #<child-1-issue-number>
3. #<child-3-issue-number> Add Slack connection step to workspace onboarding - AFK - blocked by #<child-1-issue-number>
4. #<child-4-issue-number> Add first project setup step to workspace onboarding - AFK - blocked by #<child-1-issue-number>

Notes:
- Dry run only; issue numbers and GraphQL node IDs are placeholders.
- After the design review lands, the three AFK slices can be worked in parallel.

## Issue graph

- Parent tracker: Workspace onboarding for new admins
- Wave 1: Review workspace onboarding UI before implementation (HITL)
- Wave 2: Add teammate invite step to workspace onboarding (AFK)
- Wave 2: Add Slack connection step to workspace onboarding (AFK)
- Wave 2: Add first project setup step to workspace onboarding (AFK)

## Draft parent issue body

```markdown
## Source

Add workspace onboarding that guides a new admin through inviting teammates, connecting Slack, and completing the first project setup. A design review is required before changing the onboarding UI.

## Task graph

- [ ] Review workspace onboarding UI before implementation - HITL - blocked by none
- [ ] Add teammate invite step to workspace onboarding - AFK - blocked by Review workspace onboarding UI before implementation
- [ ] Add Slack connection step to workspace onboarding - AFK - blocked by Review workspace onboarding UI before implementation
- [ ] Add first project setup step to workspace onboarding - AFK - blocked by Review workspace onboarding UI before implementation

## How to grab work

Start with any unchecked AFK issue marked "None - can start immediately" in its Blocked by section. HITL issues require the named human decision or review before implementation.
```

## Draft child issue bodies

### 1. Review workspace onboarding UI before implementation

```markdown
## Parent

#<parent-issue-number>

## What to build

Review and approve the onboarding UI approach for the new workspace onboarding flow so implementation can add guided steps for teammate invites, Slack connection, and first project setup without rework.

## Type

HITL

## Acceptance criteria

- [ ] A design review covers the new onboarding flow for invite teammates, connect Slack, and first project setup.
- [ ] The approved outcome records any copy, layout, or state-transition constraints implementation must follow.
- [ ] Open design questions that would block implementation are resolved or explicitly called out.

## Verification

- [ ] Tests pass: `<not applicable for review-only issue>`
- [ ] Build succeeds: `<not applicable for review-only issue>`
- [ ] Manual check: A designer or product owner confirms the approved onboarding UI direction is ready for implementation.

## Blocked by

None - can start immediately

## User stories covered

Not explicit in source

## Files likely touched

- `src/onboarding/workspace-onboarding.tsx`
- `src/onboarding/steps/*`
- `docs/onboarding/workspace-onboarding-spec.md`

## Estimated scope

Small: 1-2 files
```

### 2. Add teammate invite step to workspace onboarding

```markdown
## Parent

#<parent-issue-number>

## What to build

Add an onboarding step that guides a new admin through inviting teammates from the workspace onboarding flow, including the step UI, invite submission path, and success state so the admin can move to the next onboarding action.

## Type

AFK

## Acceptance criteria

- [ ] The onboarding flow includes a teammate invite step for a new admin with clear next-step guidance.
- [ ] Invites submitted from onboarding create the same result as the existing teammate invite path or the new intended invite behavior.
- [ ] The onboarding step shows a success or skip state that lets the admin continue through onboarding.

## Verification

- [ ] Tests pass: `<targeted test command>`
- [ ] Build succeeds: `<build command, if known>`
- [ ] Manual check: Start workspace onboarding as a new admin, send at least one teammate invite, and confirm the flow advances without losing progress.

## Blocked by

- Blocked by #<child-1-issue-number>

## User stories covered

Not explicit in source

## Files likely touched

- `src/onboarding/steps/invite-teammates.tsx`
- `src/onboarding/api/invitations.ts`
- `tests/onboarding/invite-teammates.test.ts`

## Estimated scope

Medium: 3-5 files
```

### 3. Add Slack connection step to workspace onboarding

```markdown
## Parent

#<parent-issue-number>

## What to build

Add an onboarding step that guides a new admin through connecting Slack from the workspace onboarding flow, including the step UI, integration handoff, and connected state so the admin can continue onboarding after Slack is linked or intentionally skipped.

## Type

AFK

## Acceptance criteria

- [ ] The onboarding flow includes a Slack connection step with clear guidance about what happens next.
- [ ] Completing the Slack connection from onboarding reaches the expected connected state or handles a deliberate skip path.
- [ ] The onboarding flow resumes correctly after the Slack connection attempt.

## Verification

- [ ] Tests pass: `<targeted test command>`
- [ ] Build succeeds: `<build command, if known>`
- [ ] Manual check: Start workspace onboarding as a new admin, connect Slack or use the supported skip path, and confirm onboarding returns to the correct next step.

## Blocked by

- Blocked by #<child-1-issue-number>

## User stories covered

Not explicit in source

## Files likely touched

- `src/onboarding/steps/connect-slack.tsx`
- `src/integrations/slack/oauth.ts`
- `tests/onboarding/connect-slack.test.ts`

## Estimated scope

Medium: 3-5 files
```

### 4. Add first project setup step to workspace onboarding

```markdown
## Parent

#<parent-issue-number>

## What to build

Add an onboarding step that guides a new admin through creating the first project from the workspace onboarding flow, including the step UI, project creation path, and completion state so onboarding can end with a usable first project.

## Type

AFK

## Acceptance criteria

- [ ] The onboarding flow includes a first project setup step with enough guidance for a new admin to complete it.
- [ ] Completing the step creates the first project using the intended project setup path.
- [ ] The onboarding flow shows a completion state once the first project is created or the supported completion path is reached.

## Verification

- [ ] Tests pass: `<targeted test command>`
- [ ] Build succeeds: `<build command, if known>`
- [ ] Manual check: Start workspace onboarding as a new admin, create the first project from onboarding, and confirm the flow ends in a completed state with the project available.

## Blocked by

- Blocked by #<child-1-issue-number>

## User stories covered

Not explicit in source

## Files likely touched

- `src/onboarding/steps/first-project-setup.tsx`
- `src/projects/create-project.ts`
- `tests/onboarding/first-project-setup.test.ts`

## Estimated scope

Medium: 3-5 files
```

## Draft commands

```bash
# Create parent tracker
gh issue create   --title "Workspace onboarding for new admins"   --body-file /home/adam/dev/personal/skills/skills/prd-to-tasks-workspace/iteration-1/eval-2-hitl-onboarding-waves/old_skill/run-1/outputs/parent-issue.md

# Create child issues in dependency order
gh issue create   --title "Review workspace onboarding UI before implementation"   --body-file /home/adam/dev/personal/skills/skills/prd-to-tasks-workspace/iteration-1/eval-2-hitl-onboarding-waves/old_skill/run-1/outputs/child-1-review-workspace-onboarding-ui-before-implementation.md

gh issue create   --title "Add teammate invite step to workspace onboarding"   --body-file /home/adam/dev/personal/skills/skills/prd-to-tasks-workspace/iteration-1/eval-2-hitl-onboarding-waves/old_skill/run-1/outputs/child-2-add-teammate-invite-step-to-workspace-onboarding.md

gh issue create   --title "Add Slack connection step to workspace onboarding"   --body-file /home/adam/dev/personal/skills/skills/prd-to-tasks-workspace/iteration-1/eval-2-hitl-onboarding-waves/old_skill/run-1/outputs/child-3-add-slack-connection-step-to-workspace-onboarding.md

gh issue create   --title "Add first project setup step to workspace onboarding"   --body-file /home/adam/dev/personal/skills/skills/prd-to-tasks-workspace/iteration-1/eval-2-hitl-onboarding-waves/old_skill/run-1/outputs/child-4-add-first-project-setup-step-to-workspace-onboarding.md

# Attach child issues after creation
PARENT_ISSUE_ID=$(gh issue view <parent-issue-number> --json id --jq .id)
CHILD_ISSUE_ID=$(gh issue view <child-1-issue-number> --json id --jq .id)
gh api graphql -f query="
mutation {
  addSubIssue(input: {issueId: "$PARENT_ISSUE_ID", subIssueId: "$CHILD_ISSUE_ID"}) {
    issue { number }
  }
}"

PARENT_ISSUE_ID=$(gh issue view <parent-issue-number> --json id --jq .id)
CHILD_ISSUE_ID=$(gh issue view <child-2-issue-number> --json id --jq .id)
gh api graphql -f query="
mutation {
  addSubIssue(input: {issueId: "$PARENT_ISSUE_ID", subIssueId: "$CHILD_ISSUE_ID"}) {
    issue { number }
  }
}"

PARENT_ISSUE_ID=$(gh issue view <parent-issue-number> --json id --jq .id)
CHILD_ISSUE_ID=$(gh issue view <child-3-issue-number> --json id --jq .id)
gh api graphql -f query="
mutation {
  addSubIssue(input: {issueId: "$PARENT_ISSUE_ID", subIssueId: "$CHILD_ISSUE_ID"}) {
    issue { number }
  }
}"

PARENT_ISSUE_ID=$(gh issue view <parent-issue-number> --json id --jq .id)
CHILD_ISSUE_ID=$(gh issue view <child-4-issue-number> --json id --jq .id)
gh api graphql -f query="
mutation {
  addSubIssue(input: {issueId: "$PARENT_ISSUE_ID", subIssueId: "$CHILD_ISSUE_ID"}) {
    issue { number }
  }
}"
```
