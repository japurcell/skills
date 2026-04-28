## Proposed vertical-slice breakdown (present first)

1. **Title**: Draft onboarding flow design and review
   **Type**: HITL
   **Execution wave**: W1
   **Blocked by**: None
   **User stories covered**: Not explicit in source
2. **Title**: Implement workspace onboarding UI (invite teammates, connect Slack, project setup)
   **Type**: AFK
   **Execution wave**: W2
   **Blocked by**: Slice 1: Draft onboarding flow design and review
   **User stories covered**: Not explicit in source

---

## Child issue draft 1

### Title: Draft onboarding flow design and review

## Parent
#<parent-issue-number>

## What to build
Draft the new workspace onboarding flow, including steps for inviting teammates, connecting Slack, and completing the first project setup. Present the design for review and approval before implementation.

## Type
HITL

## Acceptance criteria
- [ ] Design mockups for each onboarding step are created
- [ ] Design reviewed and approved by product/design lead
- [ ] Feedback from review is incorporated

## Verification
- [ ] Manual check: Product/design lead reviews and approves mockups
- [ ] Design artifacts are attached to the issue or linked

## Blocked by
None - can start immediately

## Queue position
- Parent queue: direct subissue of #<parent-issue-number>
- Execution wave: W1
- Ready to start when: this issue has no blockers

## User stories covered
Not explicit in source

## Files likely touched
- `designs/onboarding-flow/`
- `docs/onboarding.md`

## Estimated scope
Medium: 3-5 files

---

## Child issue draft 2

### Title: Implement workspace onboarding UI (invite teammates, connect Slack, project setup)

## Parent
#<parent-issue-number>

## What to build
Implement the onboarding UI for new workspace admins, guiding them through inviting teammates, connecting Slack, and completing the first project setup, based on the approved design.

## Type
AFK

## Acceptance criteria
- [ ] UI implements all onboarding steps as per approved design
- [ ] Teammate invitation flow is functional
- [ ] Slack connection step is integrated
- [ ] First project setup is guided and completes successfully

## Verification
- [ ] Tests pass: `npm test onboarding`
- [ ] Build succeeds: `npm run build`
- [ ] Manual check: Complete onboarding as a new admin in a test workspace

## Blocked by
- Blocked by #<child-1>

## Queue position
- Parent queue: direct subissue of #<parent-issue-number>
- Execution wave: W2
- Ready to start when: #<child-1> is closed

## User stories covered
Not explicit in source

## Files likely touched
- `src/onboarding/`
- `src/integrations/slack/`
- `src/projects/`
- `tests/onboarding.test.ts`

## Estimated scope
Large: 5+ files

---

## Managed parent-body block

<!-- prd-to-tasks:start -->

## Task graph

- [ ] W1 - #<child-1> Draft onboarding flow design and review - HITL - blocked by none
- [ ] W2 - #<child-2> Implement workspace onboarding UI (invite teammates, connect Slack, project setup) - AFK - blocked by #<child-1>

## How to grab work

1. Open this parent issue and inspect its direct subissues.
2. The executable work is in the sibling implementation issues listed above.
3. Pick any open AFK issue in the lowest-numbered wave whose blockers are all closed.
4. If several AFK issues are ready in the same wave, they may be worked in parallel.
5. Do not start HITL issues until the named human decision or review has happened.
<!-- prd-to-tasks:end -->

---

## Subissue attachment commands

```bash
# Attach child 1
PARENT_ISSUE_ID=$(gh issue view <parent-issue-number> --json id --jq .id)
CHILD_ISSUE_ID=$(gh issue view <child-1> --json id --jq .id)
gh api graphql -f query="
mutation {
  addSubIssue(input: {issueId: \"$PARENT_ISSUE_ID\", subIssueId: \"$CHILD_ISSUE_ID\"}) {
    issue { number }
  }
}"

# Attach child 2
CHILD_ISSUE_ID=$(gh issue view <child-2> --json id --jq .id)
gh api graphql -f query="
mutation {
  addSubIssue(input: {issueId: \"$PARENT_ISSUE_ID\", subIssueId: \"$CHILD_ISSUE_ID\"}) {
    issue { number }
  }
}"
```

---

## Final summary

Created task graph for workspace onboarding (invite teammates, connect Slack, first project setup).

Parent: #<parent-issue-number> Workspace onboarding tracker

Child issues:

1. #<child-1> Draft onboarding flow design and review - W1 - HITL - blocked by none
2. #<child-2> Implement workspace onboarding UI (invite teammates, connect Slack, project setup) - W2 - AFK - blocked by #<child-1>

How to grab work:

- Open parent #<parent-issue-number> and inspect its direct subissues.
- Pick the lowest-numbered open AFK wave whose blockers are all closed.
- If the parent issue already existed, read the managed `Task graph` / `How to grab work` section in its body.

Notes:
- Design review (HITL) is required before UI implementation.
- All issue numbers are placeholders for draft only.
