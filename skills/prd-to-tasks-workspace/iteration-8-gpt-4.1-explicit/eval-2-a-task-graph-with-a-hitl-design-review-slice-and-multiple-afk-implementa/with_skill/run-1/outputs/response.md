## Parent tracker draft

### Title
Add workspace onboarding for new admins

### Body

## Source

Add workspace onboarding that guides a new admin through inviting teammates, connecting Slack, and completing the first project setup. We need design review before changing the onboarding UI.

## Task graph

- [ ] W1 - Draft onboarding flow design - HITL - blocked by none
- [ ] W2 - Implement teammate invitation step - AFK - blocked by #<child-1>
- [ ] W2 - Implement Slack connection step - AFK - blocked by #<child-1>
- [ ] W2 - Implement first project setup step - AFK - blocked by #<child-1>

## How to grab work

Work is executed from this issue's direct subissues. Start with any open AFK issue in the lowest-numbered wave whose blockers are all closed. If multiple AFK issues share that wave and do not block one another, they may be worked in parallel. HITL issues require the named human decision or review before implementation.

---

## Child issue draft 1

## Parent

#<parent-issue-number>

## What to build

Draft and review the onboarding flow design for new admin onboarding, covering teammate invitation, Slack connection, and first project setup. This design must be reviewed and approved before UI implementation.

## Type

HITL

## Acceptance criteria

- [ ] Onboarding flow design covers all required steps
- [ ] Design reviewed and approved by product/design lead
- [ ] Feedback from review is incorporated

## Verification

- [ ] Manual check: Product/design lead reviews and approves the design

## Blocked by

None - can start immediately

## Queue position

- Parent queue: direct subissue of #<parent-issue-number>
- Execution wave: W1
- Ready to start when: this issue has no blockers, or every issue listed in `Blocked by` is closed

## User stories covered

Not explicit in source

## Files likely touched

- `designs/onboarding-flow.sketch`
- `docs/onboarding-flow.md`

## Estimated scope

Small: 1-2 files

---

## Child issue draft 2

## Parent

#<parent-issue-number>

## What to build

Implement the teammate invitation step in the onboarding flow, allowing a new admin to invite teammates as part of workspace setup.

## Type

AFK

## Acceptance criteria

- [ ] UI for inviting teammates is present in onboarding
- [ ] Invited teammates receive invitation emails
- [ ] Invited teammates appear in workspace member list

## Verification

- [ ] Tests pass: `<targeted UI/component test command>`
- [ ] Build succeeds: `<relevant build command>`
- [ ] Manual check: New admin can invite teammates and see them in the member list

## Blocked by

- Blocked by #<child-1>

## Queue position

- Parent queue: direct subissue of #<parent-issue-number>
- Execution wave: W2
- Ready to start when: #<child-1> is closed

## User stories covered

Not explicit in source

## Files likely touched

- `src/onboarding/InviteTeammates.tsx`
- `src/api/invite.ts`
- `tests/onboarding/invite.test.ts`

## Estimated scope

Medium: 3-5 files

---

## Child issue draft 3

## Parent

#<parent-issue-number>

## What to build

Implement the Slack connection step in the onboarding flow, allowing a new admin to connect Slack as part of workspace setup.

## Type

AFK

## Acceptance criteria

- [ ] UI for connecting Slack is present in onboarding
- [ ] Slack OAuth flow completes successfully
- [ ] Connected Slack workspace is shown in settings

## Verification

- [ ] Tests pass: `<targeted UI/component test command>`
- [ ] Build succeeds: `<relevant build command>`
- [ ] Manual check: New admin can connect Slack and see it in workspace settings

## Blocked by

- Blocked by #<child-1>

## Queue position

- Parent queue: direct subissue of #<parent-issue-number>
- Execution wave: W2
- Ready to start when: #<child-1> is closed

## User stories covered

Not explicit in source

## Files likely touched

- `src/onboarding/ConnectSlack.tsx`
- `src/api/slack.ts`
- `tests/onboarding/slack.test.ts`

## Estimated scope

Medium: 3-5 files

---

## Child issue draft 4

## Parent

#<parent-issue-number>

## What to build

Implement the first project setup step in the onboarding flow, allowing a new admin to create and configure the first project as part of workspace setup.

## Type

AFK

## Acceptance criteria

- [ ] UI for first project setup is present in onboarding
- [ ] New project is created and appears in project list
- [ ] Project configuration options are available during setup

## Verification

- [ ] Tests pass: `<targeted UI/component test command>`
- [ ] Build succeeds: `<relevant build command>`
- [ ] Manual check: New admin can create and configure the first project during onboarding

## Blocked by

- Blocked by #<child-1>

## Queue position

- Parent queue: direct subissue of #<parent-issue-number>
- Execution wave: W2
- Ready to start when: #<child-1> is closed

## User stories covered

Not explicit in source

## Files likely touched

- `src/onboarding/FirstProject.tsx`
- `src/api/project.ts`
- `tests/onboarding/project.test.ts`

## Estimated scope

Medium: 3-5 files

---

## Subissue attachment commands

```bash
# After creating issues, attach each child to the parent:
PARENT_ISSUE_ID=$(gh issue view <parent-issue-number> --json id --jq .id)
CHILD_ISSUE_ID_1=$(gh issue view <child-1> --json id --jq .id)
CHILD_ISSUE_ID_2=$(gh issue view <child-2> --json id --jq .id)
CHILD_ISSUE_ID_3=$(gh issue view <child-3> --json id --jq .id)
CHILD_ISSUE_ID_4=$(gh issue view <child-4> --json id --jq .id)
gh api graphql -f query="
mutation {
  addSubIssue(input: {issueId: \"$PARENT_ISSUE_ID\", subIssueId: \"$CHILD_ISSUE_ID_1\"}) { issue { number } }
  addSubIssue(input: {issueId: \"$PARENT_ISSUE_ID\", subIssueId: \"$CHILD_ISSUE_ID_2\"}) { issue { number } }
  addSubIssue(input: {issueId: \"$PARENT_ISSUE_ID\", subIssueId: \"$CHILD_ISSUE_ID_3\"}) { issue { number } }
  addSubIssue(input: {issueId: \"$PARENT_ISSUE_ID\", subIssueId: \"$CHILD_ISSUE_ID_4\"}) { issue { number } }
}"
```

---

## Final summary

Created task graph for workspace onboarding for new admins.

Parent: #<parent-issue-number> Add workspace onboarding for new admins

Child issues:

1. #<child-1> Draft onboarding flow design - W1 - HITL - blocked by none
2. #<child-2> Implement teammate invitation step - W2 - AFK - blocked by #<child-1>
3. #<child-3> Implement Slack connection step - W2 - AFK - blocked by #<child-1>
4. #<child-4> Implement first project setup step - W2 - AFK - blocked by #<child-1>

How to grab work:

- Open parent #<parent-issue-number> and inspect its direct subissues.
- Pick the lowest-numbered open AFK wave whose blockers are all closed.
- Read the managed `Task graph` / `How to grab work` section in its body.

Notes:

- Design review (HITL) is required before implementation.
- All implementation slices are AFK and can proceed in parallel after design approval.
