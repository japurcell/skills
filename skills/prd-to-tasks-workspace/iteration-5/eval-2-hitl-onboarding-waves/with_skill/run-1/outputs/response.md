# Parent Tracker Issue (Draft)

## Source

Add workspace onboarding that guides a new admin through inviting teammates, connecting Slack, and completing the first project setup. We need design review before changing the onboarding UI.

## Task graph

- [ ] W1 - #<issue-design-review> Onboarding UI design review - HITL - blocked by none
- [ ] W2 - #<issue-invite-teammates> Implement teammate invitation onboarding - AFK - blocked by #<issue-design-review>
- [ ] W2 - #<issue-connect-slack> Implement Slack connection onboarding - AFK - blocked by #<issue-design-review>
- [ ] W2 - #<issue-project-setup> Implement first project setup onboarding - AFK - blocked by #<issue-design-review>

## How to grab work

Work is executed from this issue's direct subissues. Start with any open AFK issue in the lowest-numbered wave whose blockers are all closed. If multiple AFK issues share that wave and do not block one another, they may be worked in parallel. HITL issues require the named human decision or review before implementation.

---

## Child Issue Drafts

---
### Onboarding UI design review

```
## Parent

#<parent-issue-number>

## What to build

Conduct a design review of the proposed workspace onboarding UI before any implementation begins. Review should cover flows for inviting teammates, connecting Slack, and first project setup.

## Type

HITL

## Acceptance criteria

- [ ] Design review is scheduled with the appropriate stakeholders
- [ ] Feedback is documented and actionable
- [ ] Approval is granted before implementation

## Verification

- [ ] Manual check: Review meeting held and feedback documented

## Blocked by

None - can start immediately

## Queue position

- Parent queue: direct subissue of #<parent-issue-number>
- Execution wave: W1
- Ready to start when: this issue has no blockers

## User stories covered

Not explicit in source

## Files likely touched

- `design/onboarding-mockups.fig`

## Estimated scope

Small: 1-2 files
```

---
### Implement teammate invitation onboarding

```
## Parent

#<parent-issue-number>

## What to build

Implement the onboarding step that guides a new admin through inviting teammates to the workspace.

## Type

AFK

## Acceptance criteria

- [ ] Admin is prompted to invite teammates during onboarding
- [ ] Invitations can be sent via email
- [ ] UI reflects invitation status

## Verification

- [ ] Tests pass: `npm test`
- [ ] Build succeeds: `npm run build`
- [ ] Manual check: Invite teammates as a new admin

## Blocked by

- Blocked by #<issue-design-review>

## Queue position

- Parent queue: direct subissue of #<parent-issue-number>
- Execution wave: W2
- Ready to start when: #<issue-design-review> is closed

## User stories covered

Not explicit in source

## Files likely touched

- `src/onboarding/InviteTeammates.tsx`
- `tests/onboarding/InviteTeammates.test.ts`

## Estimated scope

Medium: 3-5 files
```

---
### Implement Slack connection onboarding

```
## Parent

#<parent-issue-number>

## What to build

Implement the onboarding step that guides a new admin through connecting Slack to the workspace.

## Type

AFK

## Acceptance criteria

- [ ] Admin is prompted to connect Slack during onboarding
- [ ] Slack OAuth flow is integrated
- [ ] UI confirms successful connection

## Verification

- [ ] Tests pass: `npm test`
- [ ] Build succeeds: `npm run build`
- [ ] Manual check: Connect Slack as a new admin

## Blocked by

- Blocked by #<issue-design-review>

## Queue position

- Parent queue: direct subissue of #<parent-issue-number>
- Execution wave: W2
- Ready to start when: #<issue-design-review> is closed

## User stories covered

Not explicit in source

## Files likely touched

- `src/onboarding/ConnectSlack.tsx`
- `tests/onboarding/ConnectSlack.test.ts`

## Estimated scope

Medium: 3-5 files
```

---
### Implement first project setup onboarding

```
## Parent

#<parent-issue-number>

## What to build

Implement the onboarding step that guides a new admin through setting up their first project.

## Type

AFK

## Acceptance criteria

- [ ] Admin is prompted to set up a project during onboarding
- [ ] Project setup flow is clear and actionable
- [ ] UI confirms successful project creation

## Verification

- [ ] Tests pass: `npm test`
- [ ] Build succeeds: `npm run build`
- [ ] Manual check: Complete first project setup as a new admin

## Blocked by

- Blocked by #<issue-design-review>

## Queue position

- Parent queue: direct subissue of #<parent-issue-number>
- Execution wave: W2
- Ready to start when: #<issue-design-review> is closed

## User stories covered

Not explicit in source

## Files likely touched

- `src/onboarding/ProjectSetup.tsx`
- `tests/onboarding/ProjectSetup.test.ts`

## Estimated scope

Medium: 3-5 files
```

---

## Subissue attachment commands (draft)

```
# For each child issue, after creation:
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

## Summary

Created task graph for workspace onboarding with design review gate.

Parent: #<parent-issue-number> (draft)

Child issues:

1. #<issue-design-review> Onboarding UI design review - W1 - HITL - blocked by none
2. #<issue-invite-teammates> Implement teammate invitation onboarding - W2 - AFK - blocked by #<issue-design-review>
3. #<issue-connect-slack> Implement Slack connection onboarding - W2 - AFK - blocked by #<issue-design-review>
4. #<issue-project-setup> Implement first project setup onboarding - W2 - AFK - blocked by #<issue-design-review>

How to grab work:
- Open parent #<parent-issue-number> and inspect its direct subissues.
- Pick the lowest-numbered open AFK wave whose blockers are all closed.
- Read the managed `Task graph` / `How to grab work` section in the parent issue body.

Notes:
- All issue numbers are placeholders.
- No GitHub mutations or code implementations were performed (dry run).
