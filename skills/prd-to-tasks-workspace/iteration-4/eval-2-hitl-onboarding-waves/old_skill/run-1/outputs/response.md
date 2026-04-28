# Drafted Task Graph for Workspace Onboarding (Dry Run)

**Note:** This is a dry-run draft. All issue numbers are placeholders (e.g., #<parent-issue-number>, #<child-issue-number>). No GitHub mutations have been performed.

## Parent Tracker Issue (Draft)

### Title
Workspace Onboarding: Invite Teammates, Connect Slack, Complete First Project, and UI Design Review

### Body

#### Source
Add workspace onboarding that guides a new admin through inviting teammates, connecting Slack, and completing the first project setup. We need design review before changing the onboarding UI.

#### Task graph
- [ ] W1 - Design review for onboarding UI changes - HITL - blocked by none
- [ ] W2 - Implement teammate invitation onboarding step - AFK - blocked by #<child-issue-1>
- [ ] W2 - Implement Slack connection onboarding step - AFK - blocked by #<child-issue-1>
- [ ] W2 - Implement first project setup onboarding step - AFK - blocked by #<child-issue-1>

#### How to grab work
Work is executed from this issue's direct subissues. Start with any open AFK issue in the lowest-numbered wave whose blockers are all closed. If multiple AFK issues share that wave and do not block one another, they may be worked in parallel. HITL issues require the named human decision or review before implementation.

---

## Child Issues (Draft)

### 1. Design review for onboarding UI changes
**Parent:** #<parent-issue-number>
**Type:** HITL
**Execution wave:** W1
**Blocked by:** None
**User stories covered:** UI design review before onboarding changes

#### What to build
Conduct a design review of the proposed onboarding UI changes. Approve or provide feedback before implementation begins.

#### Acceptance criteria
- [ ] Design review is completed by the designated reviewer
- [ ] Feedback is documented and actionable
- [ ] Approval or required changes are clearly communicated

#### Verification
- [ ] Manual check: Reviewer confirms review is complete and feedback is addressed

#### Files likely touched
- `design/onboarding/`
- `docs/onboarding/`

#### Estimated scope
Small: 1-2 files

#### Queue position
- Parent queue: direct subissue of #<parent-issue-number>
- Execution wave: W1
- Ready to start when: this issue has no blockers

---

### 2. Implement teammate invitation onboarding step
**Parent:** #<parent-issue-number>
**Type:** AFK
**Execution wave:** W2
**Blocked by:** #<child-issue-1>
**User stories covered:** Guide admin to invite teammates during onboarding

#### What to build
Implement the onboarding step that guides a new admin through inviting teammates to the workspace.

#### Acceptance criteria
- [ ] Admins are prompted to invite teammates during onboarding
- [ ] Invitations are sent and tracked
- [ ] UI matches approved design

#### Verification
- [ ] Tests pass: `npm test`
- [ ] Build succeeds: `npm run build`
- [ ] Manual check: Onboarding flow includes teammate invitation and works as expected

#### Files likely touched
- `src/admin/onboarding/`
- `src/api/invitations/`
- `tests/admin/onboarding/`

#### Estimated scope
Medium: 3-5 files

#### Queue position
- Parent queue: direct subissue of #<parent-issue-number>
- Execution wave: W2
- Ready to start when: #<child-issue-1> is closed

---

### 3. Implement Slack connection onboarding step
**Parent:** #<parent-issue-number>
**Type:** AFK
**Execution wave:** W2
**Blocked by:** #<child-issue-1>
**User stories covered:** Guide admin to connect Slack during onboarding

#### What to build
Implement the onboarding step that guides a new admin through connecting Slack to the workspace.

#### Acceptance criteria
- [ ] Admins are prompted to connect Slack during onboarding
- [ ] Slack integration is verified and confirmed
- [ ] UI matches approved design

#### Verification
- [ ] Tests pass: `npm test`
- [ ] Build succeeds: `npm run build`
- [ ] Manual check: Onboarding flow includes Slack connection and works as expected

#### Files likely touched
- `src/admin/onboarding/`
- `src/integrations/slack/`
- `tests/admin/onboarding/`

#### Estimated scope
Medium: 3-5 files

#### Queue position
- Parent queue: direct subissue of #<parent-issue-number>
- Execution wave: W2
- Ready to start when: #<child-issue-1> is closed

---

### 4. Implement first project setup onboarding step
**Parent:** #<parent-issue-number>
**Type:** AFK
**Execution wave:** W2
**Blocked by:** #<child-issue-1>
**User stories covered:** Guide admin to complete first project setup during onboarding

#### What to build
Implement the onboarding step that guides a new admin through completing the first project setup.

#### Acceptance criteria
- [ ] Admins are prompted to set up their first project during onboarding
- [ ] Project setup is completed and confirmed
- [ ] UI matches approved design

#### Verification
- [ ] Tests pass: `npm test`
- [ ] Build succeeds: `npm run build`
- [ ] Manual check: Onboarding flow includes project setup and works as expected

#### Files likely touched
- `src/admin/onboarding/`
- `src/api/projects/`
- `tests/admin/onboarding/`

#### Estimated scope
Medium: 3-5 files

#### Queue position
- Parent queue: direct subissue of #<parent-issue-number>
- Execution wave: W2
- Ready to start when: #<child-issue-1> is closed

---

## Summary
Created task graph for workspace onboarding (draft, dry-run).

Parent: #<parent-issue-number> Workspace Onboarding: Invite Teammates, Connect Slack, Complete First Project, and UI Design Review

Child issues:
1. #<child-issue-1> Design review for onboarding UI changes - W1 - HITL - blocked by none
2. #<child-issue-2> Implement teammate invitation onboarding step - W2 - AFK - blocked by #<child-issue-1>
3. #<child-issue-3> Implement Slack connection onboarding step - W2 - AFK - blocked by #<child-issue-1>
4. #<child-issue-4> Implement first project setup onboarding step - W2 - AFK - blocked by #<child-issue-1>

How to grab work:
- Open parent #<parent-issue-number> and inspect its direct subissues.
- Pick the lowest-numbered open AFK wave whose blockers are all closed.
- Read the managed `Task graph` / `How to grab work` section in the parent body.

Notes:
- All issue numbers are placeholders.
- No GitHub mutations have been performed.
- Design review (HITL) is required before implementation.
- All implementation slices are AFK and can proceed in parallel after design review.
