# Drafted Task Graph for Workspace Onboarding (Dry Run)

## Proposed vertical-slice breakdown (present first)

1. **Title**: Design review for onboarding UI changes
   **Type**: HITL
   **Execution wave**: W1
   **Blocked by**: None
   **User stories covered**: Not explicit in source
2. **Title**: Implement admin onboarding flow: invite teammates
   **Type**: AFK
   **Execution wave**: W2
   **Blocked by**: Slice 1: Design review for onboarding UI changes
   **User stories covered**: Not explicit in source
3. **Title**: Implement admin onboarding flow: connect Slack
   **Type**: AFK
   **Execution wave**: W2
   **Blocked by**: Slice 1: Design review for onboarding UI changes
   **User stories covered**: Not explicit in source
4. **Title**: Implement admin onboarding flow: complete first project setup
   **Type**: AFK
   **Execution wave**: W2
   **Blocked by**: Slice 1: Design review for onboarding UI changes
   **User stories covered**: Not explicit in source

---

## Child Issue Drafts

### 1. Design review for onboarding UI changes

```
## Parent

#<parent-issue-number>

## What to build

Conduct a design review of the proposed onboarding UI changes to ensure usability and visual consistency before implementation.

## Type

HITL

## Acceptance criteria

- [ ] Design mockups reviewed by designated reviewer
- [ ] Feedback documented and actionable
- [ ] Approval recorded in issue comments

## Verification

- [ ] Manual check: Reviewer confirms approval in this issue

## Blocked by

None - can start immediately

## Queue position

- Parent queue: direct subissue of #<parent-issue-number>
- Execution wave: W1
- Ready to start when: this issue has no blockers

## User stories covered

Not explicit in source

## Files likely touched

- `designs/onboarding-mockups/`

## Estimated scope

Small: 1-2 files
```

### 2. Implement admin onboarding flow: invite teammates

```
## Parent

#<parent-issue-number>

## What to build

Implement the onboarding step that guides a new admin through inviting teammates to the workspace.

## Type

AFK

## Acceptance criteria

- [ ] UI displays clear instructions for inviting teammates
- [ ] Invitation emails are sent successfully
- [ ] Invited users appear in the workspace member list

## Verification

- [ ] Tests pass: `<frontend and backend test command>`
- [ ] Build succeeds: `<build command>`
- [ ] Manual check: Admin can invite and see new teammates in the UI

## Blocked by

- Blocked by #<design-review-issue-number>

## Queue position

- Parent queue: direct subissue of #<parent-issue-number>
- Execution wave: W2
- Ready to start when: #<design-review-issue-number> is closed

## User stories covered

Not explicit in source

## Files likely touched

- `src/onboarding/InviteTeammates.tsx`
- `src/api/invitations.ts`
- `tests/onboarding/invite.test.ts`

## Estimated scope

Medium: 3-5 files
```

### 3. Implement admin onboarding flow: connect Slack

```
## Parent

#<parent-issue-number>

## What to build

Implement the onboarding step that guides a new admin through connecting Slack to the workspace.

## Type

AFK

## Acceptance criteria

- [ ] UI displays Slack connection option
- [ ] OAuth flow completes successfully
- [ ] Slack integration status is visible in the workspace settings

## Verification

- [ ] Tests pass: `<frontend and integration test command>`
- [ ] Build succeeds: `<build command>`
- [ ] Manual check: Admin can connect Slack and see integration status

## Blocked by

- Blocked by #<design-review-issue-number>

## Queue position

- Parent queue: direct subissue of #<parent-issue-number>
- Execution wave: W2
- Ready to start when: #<design-review-issue-number> is closed

## User stories covered

Not explicit in source

## Files likely touched

- `src/onboarding/ConnectSlack.tsx`
- `src/integrations/slack.ts`
- `tests/onboarding/slack.test.ts`

## Estimated scope

Medium: 3-5 files
```

### 4. Implement admin onboarding flow: complete first project setup

```
## Parent

#<parent-issue-number>

## What to build

Implement the onboarding step that guides a new admin through completing the first project setup in the workspace.

## Type

AFK

## Acceptance criteria

- [ ] UI guides admin through project creation
- [ ] Project appears in workspace dashboard
- [ ] Success confirmation is shown

## Verification

- [ ] Tests pass: `<frontend and backend test command>`
- [ ] Build succeeds: `<build command>`
- [ ] Manual check: Admin can create a project and see it in the dashboard

## Blocked by

- Blocked by #<design-review-issue-number>

## Queue position

- Parent queue: direct subissue of #<parent-issue-number>
- Execution wave: W2
- Ready to start when: #<design-review-issue-number> is closed

## User stories covered

Not explicit in source

## Files likely touched

- `src/onboarding/ProjectSetup.tsx`
- `src/api/projects.ts`
- `tests/onboarding/project.test.ts`

## Estimated scope

Medium: 3-5 files
```

---

## Managed parent-body block (draft)

```
<!-- prd-to-tasks:start -->

## Task graph

- [ ] W1 - #<design-review-issue-number> Design review for onboarding UI changes - HITL - blocked by none
- [ ] W2 - #<invite-teammates-issue-number> Implement admin onboarding flow: invite teammates - AFK - blocked by #<design-review-issue-number>
- [ ] W2 - #<connect-slack-issue-number> Implement admin onboarding flow: connect Slack - AFK - blocked by #<design-review-issue-number>
- [ ] W2 - #<project-setup-issue-number> Implement admin onboarding flow: complete first project setup - AFK - blocked by #<design-review-issue-number>

## How to grab work

1. Open this parent issue and inspect its direct subissues.
2. The executable work is in the sibling implementation issues listed above.
3. Pick any open AFK issue in the lowest-numbered wave whose blockers are all closed.
4. If several AFK issues are ready in the same wave, they may be worked in parallel.
5. Do not start HITL issues until the named human decision or review has happened.
<!-- prd-to-tasks:end -->
```

---

## Subissue attachment commands (draft)

```
# Attach each child issue to the parent (replace placeholders with real numbers):
PARENT_ISSUE_ID=$(gh issue view <parent-issue-number> --json id --jq .id)
CHILD_ISSUE_ID=$(gh issue view <child-issue-number> --json id --jq .id)
gh api graphql -f query="
mutation {
  addSubIssue(input: {issueId: \"$PARENT_ISSUE_ID\", subIssueId: \"$CHILD_ISSUE_ID\"}) {
    issue { number }
  }
}"
```

---

## Final summary (draft)

Created task graph for workspace onboarding feature.

Parent: #<parent-issue-number> Workspace onboarding

Child issues:

1. #<design-review-issue-number> Design review for onboarding UI changes - W1 - HITL - blocked by none
2. #<invite-teammates-issue-number> Implement admin onboarding flow: invite teammates - W2 - AFK - blocked by #<design-review-issue-number>
3. #<connect-slack-issue-number> Implement admin onboarding flow: connect Slack - W2 - AFK - blocked by #<design-review-issue-number>
4. #<project-setup-issue-number> Implement admin onboarding flow: complete first project setup - W2 - AFK - blocked by #<design-review-issue-number>

How to grab work:

- Open parent #<parent-issue-number> and inspect its direct subissues.
- Pick the lowest-numbered open AFK wave whose blockers are all closed.
- If the parent issue already existed, read the managed `Task graph` / `How to grab work` section in its body.

Notes:

- Design review (HITL) is required before implementation.
- All implementation slices are AFK and can proceed in parallel after design review.
