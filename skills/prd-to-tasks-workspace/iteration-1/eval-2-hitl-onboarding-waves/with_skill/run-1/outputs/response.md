Created task graph for workspace onboarding that guides a new admin through inviting teammates, connecting Slack, and completing the first project setup.

Parent: #<new-parent> Workspace onboarding for new admins

Child issues:
1. #<new-child-1> Design review for workspace onboarding flow - W1 - HITL - blocked by none
2. #<new-child-2> Add teammate invite step to workspace onboarding - W2 - AFK - blocked by #<new-child-1>
3. #<new-child-3> Add Slack connection step to workspace onboarding - W3 - AFK - blocked by #<new-child-2>
4. #<new-child-4> Add first project setup step to workspace onboarding - W3 - AFK - blocked by #<new-child-2>

How to grab work:
- Open parent #<new-parent> and inspect its direct subissues.
- Pick the lowest-numbered open AFK wave whose blockers are all closed.
- No queue-guide issue is needed because this run creates a new parent tracker.

Notes:
- Dry run only: issue numbers are placeholders because no GitHub issues were created.
- The onboarding UI work is blocked on a human design review before implementation begins.
- Likely files and verification commands are drafted generically because no repository or codebase context was provided.

## Issue graph

1. **Title**: Design review for workspace onboarding flow  
   **Type**: HITL  
   **Execution wave**: W1  
   **Blocked by**: None  
   **User stories covered**: Not explicit in source
2. **Title**: Add teammate invite step to workspace onboarding  
   **Type**: AFK  
   **Execution wave**: W2  
   **Blocked by**: Slice 1: Design review for workspace onboarding flow  
   **User stories covered**: Not explicit in source
3. **Title**: Add Slack connection step to workspace onboarding  
   **Type**: AFK  
   **Execution wave**: W3  
   **Blocked by**: Slice 2: Add teammate invite step to workspace onboarding  
   **User stories covered**: Not explicit in source
4. **Title**: Add first project setup step to workspace onboarding  
   **Type**: AFK  
   **Execution wave**: W3  
   **Blocked by**: Slice 2: Add teammate invite step to workspace onboarding  
   **User stories covered**: Not explicit in source

## Parent issue draft

**Title**: Workspace onboarding for new admins

**Body**:

```markdown
## Source

Add workspace onboarding that guides a new admin through inviting teammates, connecting Slack, and completing the first project setup. A design review is required before changing the onboarding UI.

## Task graph

- [ ] W1 - Design review for workspace onboarding flow - HITL - blocked by none
- [ ] W2 - Add teammate invite step to workspace onboarding - AFK - blocked by Design review for workspace onboarding flow
- [ ] W3 - Add Slack connection step to workspace onboarding - AFK - blocked by Add teammate invite step to workspace onboarding
- [ ] W3 - Add first project setup step to workspace onboarding - AFK - blocked by Add teammate invite step to workspace onboarding

## How to grab work

Work is executed from this issue's direct subissues. Start with any open AFK issue in the lowest-numbered wave whose blockers are all closed. If multiple AFK issues share that wave and do not block one another, they may be worked in parallel. HITL issues require the named human decision or review before implementation.
```

## Child issue drafts

### #<new-child-1> Design review for workspace onboarding flow

```markdown
## Parent

#<new-parent>

## What to build

Produce and approve the workspace onboarding design for a new admin journey covering teammate invites, Slack connection, and first project setup. Capture the approved step order, UI states, copy, and any interaction details that implementation must follow.

## Type

HITL

## Acceptance criteria

- [ ] Design review is completed for the onboarding flow, including invite teammates, connect Slack, and first project setup states.
- [ ] Approved design artifacts or review notes document the step order, copy, CTA behavior, and completion states needed for implementation.
- [ ] Any unresolved questions blocking implementation are explicitly called out, or the design is approved with no blockers remaining.

## Verification

- [ ] Tests pass: `Not applicable - design review only`
- [ ] Build succeeds: `Not applicable - design review only`
- [ ] Manual check: Approved design artifacts or review notes are linked from the issue.

## Blocked by

None - can start immediately

## Queue position

- Parent queue: direct subissue of #<new-parent>
- Execution wave: W1
- Ready to start when: this issue has no blockers, or every issue listed in `Blocked by` is closed
- Parallel rule: if multiple AFK issues are ready in W1, they may be worked in parallel
- HITL rule: wait for the design review approval and any named design decision before implementation begins

## User stories covered

Not explicit in source

## Files likely touched

- `design/workspace-onboarding-flow.fig`
- `docs/onboarding/workspace-admin-flow.md`

## Estimated scope

Small: 1-2 files
```

### #<new-child-2> Add teammate invite step to workspace onboarding

```markdown
## Parent

#<new-parent>

## What to build

Add the first executable workspace onboarding step for a new admin to invite teammates. Deliver the step end to end so the onboarding entry point, invite action, step completion state, and step-specific error handling work together and allow the admin to continue after inviting teammates or explicitly skipping the step.

## Type

AFK

## Acceptance criteria

- [ ] A new admin entering workspace onboarding sees an invite teammates step with the approved copy, CTA, and skip behavior from the design review.
- [ ] Sending at least one invite or explicitly skipping updates onboarding progress and unlocks the next step in the flow.
- [ ] Tests cover invite step rendering, completion state, and error handling for failed invites.

## Verification

- [ ] Tests pass: `run the repository's targeted onboarding and invitation tests`
- [ ] Build succeeds: `run the repository's standard frontend build`
- [ ] Manual check: Start a fresh admin workspace and verify the invite step completes after invite or skip.

## Blocked by

- Blocked by #<new-child-1>

## Queue position

- Parent queue: direct subissue of #<new-parent>
- Execution wave: W2
- Ready to start when: #<new-child-1> is closed
- Parallel rule: if multiple AFK issues are ready in W2, they may be worked in parallel
- HITL rule: if this issue is HITL, wait for the named human decision or review before implementation begins

## User stories covered

Not explicit in source

## Files likely touched

- `src/features/onboarding/WorkspaceOnboarding.*`
- `src/features/onboarding/steps/InviteTeammatesStep.*`
- `src/features/invitations/*`
- `tests/onboarding/invite-teammates.*`

## Estimated scope

Medium: 3-5 files
```

### #<new-child-3> Add Slack connection step to workspace onboarding

```markdown
## Parent

#<new-parent>

## What to build

Add a workspace onboarding step that guides a new admin through connecting Slack from the onboarding flow. Deliver the step end to end so the approved onboarding UI, Slack connect action, success state, and retry or skip handling all work within the shared onboarding progress experience.

## Type

AFK

## Acceptance criteria

- [ ] A new admin can start the Slack connection step from workspace onboarding using the approved design and copy.
- [ ] Completing the Slack connection, or explicitly skipping when allowed, updates onboarding progress and preserves the correct status when the admin returns.
- [ ] Tests cover Slack step rendering, success state, and failure or retry handling.

## Verification

- [ ] Tests pass: `run the repository's targeted onboarding and Slack integration tests`
- [ ] Build succeeds: `run the repository's standard frontend build`
- [ ] Manual check: Start a fresh admin workspace and verify the Slack step records connected, skipped, or retry states correctly.

## Blocked by

- Blocked by #<new-child-2>

## Queue position

- Parent queue: direct subissue of #<new-parent>
- Execution wave: W3
- Ready to start when: #<new-child-2> is closed
- Parallel rule: if multiple AFK issues are ready in W3, they may be worked in parallel
- HITL rule: if this issue is HITL, wait for the named human decision or review before implementation begins

## User stories covered

Not explicit in source

## Files likely touched

- `src/features/onboarding/steps/ConnectSlackStep.*`
- `src/integrations/slack/*`
- `src/features/onboarding/WorkspaceOnboarding.*`
- `tests/onboarding/connect-slack.*`

## Estimated scope

Medium: 3-5 files
```

### #<new-child-4> Add first project setup step to workspace onboarding

```markdown
## Parent

#<new-parent>

## What to build

Add a workspace onboarding step that guides a new admin through completing the first project setup. Deliver the step end to end so the onboarding flow presents the approved project setup UI, persists completion, and reflects the final onboarding status once the first project is created or the setup step is otherwise completed.

## Type

AFK

## Acceptance criteria

- [ ] A new admin can complete the first project setup from workspace onboarding using the approved design and copy.
- [ ] Finishing the project setup step updates onboarding progress and marks the onboarding flow complete when all required steps are done.
- [ ] Tests cover project setup step rendering, completion state, and failure handling for incomplete setup attempts.

## Verification

- [ ] Tests pass: `run the repository's targeted onboarding and project setup tests`
- [ ] Build succeeds: `run the repository's standard frontend build`
- [ ] Manual check: Start a fresh admin workspace and verify project setup completion updates the final onboarding status.

## Blocked by

- Blocked by #<new-child-2>

## Queue position

- Parent queue: direct subissue of #<new-parent>
- Execution wave: W3
- Ready to start when: #<new-child-2> is closed
- Parallel rule: if multiple AFK issues are ready in W3, they may be worked in parallel
- HITL rule: if this issue is HITL, wait for the named human decision or review before implementation begins

## User stories covered

Not explicit in source

## Files likely touched

- `src/features/onboarding/steps/FirstProjectSetupStep.*`
- `src/features/projects/*`
- `src/features/onboarding/WorkspaceOnboarding.*`
- `tests/onboarding/first-project-setup.*`

## Estimated scope

Medium: 3-5 files
```

## Draft commands the skill would have the assistant produce

```bash
cat > ./outputs/parent_issue_body.md <<'EOF'
## Source

Add workspace onboarding that guides a new admin through inviting teammates, connecting Slack, and completing the first project setup. A design review is required before changing the onboarding UI.

## Task graph

- [ ] W1 - Design review for workspace onboarding flow - HITL - blocked by none
- [ ] W2 - Add teammate invite step to workspace onboarding - AFK - blocked by Design review for workspace onboarding flow
- [ ] W3 - Add Slack connection step to workspace onboarding - AFK - blocked by Add teammate invite step to workspace onboarding
- [ ] W3 - Add first project setup step to workspace onboarding - AFK - blocked by Add teammate invite step to workspace onboarding

## How to grab work

Work is executed from this issue's direct subissues. Start with any open AFK issue in the lowest-numbered wave whose blockers are all closed. If multiple AFK issues share that wave and do not block one another, they may be worked in parallel. HITL issues require the named human decision or review before implementation.
EOF

gh issue create --title "Workspace onboarding for new admins" --body-file ./outputs/parent_issue_body.md
# capture returned parent issue number as <new-parent>

cat > ./outputs/child_1_design_review.md <<'EOF'
## Parent

#<new-parent>

## What to build

Produce and approve the workspace onboarding design for a new admin journey covering teammate invites, Slack connection, and first project setup. Capture the approved step order, UI states, copy, and any interaction details that implementation must follow.

## Type

HITL

## Acceptance criteria

- [ ] Design review is completed for the onboarding flow, including invite teammates, connect Slack, and first project setup states.
- [ ] Approved design artifacts or review notes document the step order, copy, CTA behavior, and completion states needed for implementation.
- [ ] Any unresolved questions blocking implementation are explicitly called out, or the design is approved with no blockers remaining.

## Verification

- [ ] Tests pass: `Not applicable - design review only`
- [ ] Build succeeds: `Not applicable - design review only`
- [ ] Manual check: Approved design artifacts or review notes are linked from the issue.

## Blocked by

None - can start immediately

## Queue position

- Parent queue: direct subissue of #<new-parent>
- Execution wave: W1
- Ready to start when: this issue has no blockers, or every issue listed in `Blocked by` is closed
- Parallel rule: if multiple AFK issues are ready in W1, they may be worked in parallel
- HITL rule: wait for the design review approval and any named design decision before implementation begins

## User stories covered

Not explicit in source

## Files likely touched

- `design/workspace-onboarding-flow.fig`
- `docs/onboarding/workspace-admin-flow.md`

## Estimated scope

Small: 1-2 files
EOF

gh issue create --title "Design review for workspace onboarding flow" --body-file ./outputs/child_1_design_review.md
# capture returned issue number as <new-child-1>

cat > ./outputs/child_2_invite_step.md <<'EOF'
## Parent

#<new-parent>

## What to build

Add the first executable workspace onboarding step for a new admin to invite teammates. Deliver the step end to end so the onboarding entry point, invite action, step completion state, and step-specific error handling work together and allow the admin to continue after inviting teammates or explicitly skipping the step.

## Type

AFK

## Acceptance criteria

- [ ] A new admin entering workspace onboarding sees an invite teammates step with the approved copy, CTA, and skip behavior from the design review.
- [ ] Sending at least one invite or explicitly skipping updates onboarding progress and unlocks the next step in the flow.
- [ ] Tests cover invite step rendering, completion state, and error handling for failed invites.

## Verification

- [ ] Tests pass: `run the repository's targeted onboarding and invitation tests`
- [ ] Build succeeds: `run the repository's standard frontend build`
- [ ] Manual check: Start a fresh admin workspace and verify the invite step completes after invite or skip.

## Blocked by

- Blocked by #<new-child-1>

## Queue position

- Parent queue: direct subissue of #<new-parent>
- Execution wave: W2
- Ready to start when: #<new-child-1> is closed
- Parallel rule: if multiple AFK issues are ready in W2, they may be worked in parallel
- HITL rule: if this issue is HITL, wait for the named human decision or review before implementation begins

## User stories covered

Not explicit in source

## Files likely touched

- `src/features/onboarding/WorkspaceOnboarding.*`
- `src/features/onboarding/steps/InviteTeammatesStep.*`
- `src/features/invitations/*`
- `tests/onboarding/invite-teammates.*`

## Estimated scope

Medium: 3-5 files
EOF

gh issue create --title "Add teammate invite step to workspace onboarding" --body-file ./outputs/child_2_invite_step.md
# capture returned issue number as <new-child-2>

cat > ./outputs/child_3_slack_step.md <<'EOF'
## Parent

#<new-parent>

## What to build

Add a workspace onboarding step that guides a new admin through connecting Slack from the onboarding flow. Deliver the step end to end so the approved onboarding UI, Slack connect action, success state, and retry or skip handling all work within the shared onboarding progress experience.

## Type

AFK

## Acceptance criteria

- [ ] A new admin can start the Slack connection step from workspace onboarding using the approved design and copy.
- [ ] Completing the Slack connection, or explicitly skipping when allowed, updates onboarding progress and preserves the correct status when the admin returns.
- [ ] Tests cover Slack step rendering, success state, and failure or retry handling.

## Verification

- [ ] Tests pass: `run the repository's targeted onboarding and Slack integration tests`
- [ ] Build succeeds: `run the repository's standard frontend build`
- [ ] Manual check: Start a fresh admin workspace and verify the Slack step records connected, skipped, or retry states correctly.

## Blocked by

- Blocked by #<new-child-2>

## Queue position

- Parent queue: direct subissue of #<new-parent>
- Execution wave: W3
- Ready to start when: #<new-child-2> is closed
- Parallel rule: if multiple AFK issues are ready in W3, they may be worked in parallel
- HITL rule: if this issue is HITL, wait for the named human decision or review before implementation begins

## User stories covered

Not explicit in source

## Files likely touched

- `src/features/onboarding/steps/ConnectSlackStep.*`
- `src/integrations/slack/*`
- `src/features/onboarding/WorkspaceOnboarding.*`
- `tests/onboarding/connect-slack.*`

## Estimated scope

Medium: 3-5 files
EOF

gh issue create --title "Add Slack connection step to workspace onboarding" --body-file ./outputs/child_3_slack_step.md
# capture returned issue number as <new-child-3>

cat > ./outputs/child_4_project_setup_step.md <<'EOF'
## Parent

#<new-parent>

## What to build

Add a workspace onboarding step that guides a new admin through completing the first project setup. Deliver the step end to end so the onboarding flow presents the approved project setup UI, persists completion, and reflects the final onboarding status once the first project is created or the setup step is otherwise completed.

## Type

AFK

## Acceptance criteria

- [ ] A new admin can complete the first project setup from workspace onboarding using the approved design and copy.
- [ ] Finishing the project setup step updates onboarding progress and marks the onboarding flow complete when all required steps are done.
- [ ] Tests cover project setup step rendering, completion state, and failure handling for incomplete setup attempts.

## Verification

- [ ] Tests pass: `run the repository's targeted onboarding and project setup tests`
- [ ] Build succeeds: `run the repository's standard frontend build`
- [ ] Manual check: Start a fresh admin workspace and verify project setup completion updates the final onboarding status.

## Blocked by

- Blocked by #<new-child-2>

## Queue position

- Parent queue: direct subissue of #<new-parent>
- Execution wave: W3
- Ready to start when: #<new-child-2> is closed
- Parallel rule: if multiple AFK issues are ready in W3, they may be worked in parallel
- HITL rule: if this issue is HITL, wait for the named human decision or review before implementation begins

## User stories covered

Not explicit in source

## Files likely touched

- `src/features/onboarding/steps/FirstProjectSetupStep.*`
- `src/features/projects/*`
- `src/features/onboarding/WorkspaceOnboarding.*`
- `tests/onboarding/first-project-setup.*`

## Estimated scope

Medium: 3-5 files
EOF

gh issue create --title "Add first project setup step to workspace onboarding" --body-file ./outputs/child_4_project_setup_step.md
# capture returned issue number as <new-child-4>

PARENT_ISSUE_NUMBER=<new-parent>

CHILD_ISSUE_NUMBER=<new-child-1>
PARENT_ISSUE_ID=$(gh issue view "$PARENT_ISSUE_NUMBER" --json id --jq .id)
CHILD_ISSUE_ID=$(gh issue view "$CHILD_ISSUE_NUMBER" --json id --jq .id)
gh api graphql -f query="
mutation {
  addSubIssue(input: {issueId: \"$PARENT_ISSUE_ID\", subIssueId: \"$CHILD_ISSUE_ID\"}) {
    issue { number }
  }
}"

CHILD_ISSUE_NUMBER=<new-child-2>
PARENT_ISSUE_ID=$(gh issue view "$PARENT_ISSUE_NUMBER" --json id --jq .id)
CHILD_ISSUE_ID=$(gh issue view "$CHILD_ISSUE_NUMBER" --json id --jq .id)
gh api graphql -f query="
mutation {
  addSubIssue(input: {issueId: \"$PARENT_ISSUE_ID\", subIssueId: \"$CHILD_ISSUE_ID\"}) {
    issue { number }
  }
}"

CHILD_ISSUE_NUMBER=<new-child-3>
PARENT_ISSUE_ID=$(gh issue view "$PARENT_ISSUE_NUMBER" --json id --jq .id)
CHILD_ISSUE_ID=$(gh issue view "$CHILD_ISSUE_NUMBER" --json id --jq .id)
gh api graphql -f query="
mutation {
  addSubIssue(input: {issueId: \"$PARENT_ISSUE_ID\", subIssueId: \"$CHILD_ISSUE_ID\"}) {
    issue { number }
  }
}"

CHILD_ISSUE_NUMBER=<new-child-4>
PARENT_ISSUE_ID=$(gh issue view "$PARENT_ISSUE_NUMBER" --json id --jq .id)
CHILD_ISSUE_ID=$(gh issue view "$CHILD_ISSUE_NUMBER" --json id --jq .id)
gh api graphql -f query="
mutation {
  addSubIssue(input: {issueId: \"$PARENT_ISSUE_ID\", subIssueId: \"$CHILD_ISSUE_ID\"}) {
    issue { number }
  }
}"
```
