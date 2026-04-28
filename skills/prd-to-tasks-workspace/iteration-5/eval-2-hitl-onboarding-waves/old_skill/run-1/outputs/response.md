# Draft: Workspace Onboarding Task Graph

## Parent Tracker Issue (Draft)

**Title:** Workspace Onboarding: Invite Teammates, Connect Slack, Complete First Project Setup

**Body:**

## Source

Add workspace onboarding that guides a new admin through inviting teammates, connecting Slack, and completing the first project setup. Design review is required before onboarding UI changes.

## Task graph

- [ ] W1 - Design review for onboarding UI changes - HITL - blocked by none
- [ ] W2 - Implement teammate invitation step in onboarding - AFK - blocked by: Design review for onboarding UI changes
- [ ] W2 - Implement Slack connection step in onboarding - AFK - blocked by: Design review for onboarding UI changes
- [ ] W2 - Implement first project setup step in onboarding - AFK - blocked by: Design review for onboarding UI changes

## How to grab work

Work is executed from this issue's direct subissues. Start with any open AFK issue in the lowest-numbered wave whose blockers are all closed. If multiple AFK issues share that wave and do not block one another, they may be worked in parallel. HITL issues require the named human decision or review before implementation.

---

## Child Issues (Drafts)

### 1. Design review for onboarding UI changes

**Parent:** #<parent-issue-number>

**What to build:**
Conduct a design review for the proposed onboarding UI changes before implementation begins.

**Type:** HITL

**Acceptance criteria:**
- [ ] Design review is completed and feedback is documented
- [ ] Approval is granted to proceed with onboarding UI implementation

**Verification:**
- [ ] Manual check: Design review feedback is available and approval is recorded

**Blocked by:** None - can start immediately

**Queue position:**
- Parent queue: direct subissue of #<parent-issue-number>
- Execution wave: W1
- Ready to start when: this issue has no blockers

**User stories covered:** Not explicit in source

**Files likely touched:**
- `design/onboarding/`
- `docs/`

**Estimated scope:** Small: 1-2 files

---

### 2. Implement teammate invitation step in onboarding

**Parent:** #<parent-issue-number>

**What to build:**
Implement the onboarding step that guides a new admin through inviting teammates to the workspace.

**Type:** AFK

**Acceptance criteria:**
- [ ] Admins are guided to invite teammates during onboarding
- [ ] Invitations are sent and tracked
- [ ] UI and backend changes are coordinated

**Verification:**
- [ ] Tests pass: `<test command>`
- [ ] Build succeeds: `<build command>`
- [ ] Manual check: Teammate invitation flow works end-to-end

**Blocked by:** Design review for onboarding UI changes

**Queue position:**
- Parent queue: direct subissue of #<parent-issue-number>
- Execution wave: W2
- Ready to start when: Design review for onboarding UI changes is closed

**User stories covered:** Not explicit in source

**Files likely touched:**
- `src/onboarding/`
- `src/ui/`
- `src/api/`
- `tests/onboarding/`

**Estimated scope:** Medium: 3-5 files

---

### 3. Implement Slack connection step in onboarding

**Parent:** #<parent-issue-number>

**What to build:**
Implement the onboarding step that guides a new admin through connecting Slack to the workspace.

**Type:** AFK

**Acceptance criteria:**
- [ ] Admins are guided to connect Slack during onboarding
- [ ] Slack integration is verified
- [ ] UI and backend changes are coordinated

**Verification:**
- [ ] Tests pass: `<test command>`
- [ ] Build succeeds: `<build command>`
- [ ] Manual check: Slack connection flow works end-to-end

**Blocked by:** Design review for onboarding UI changes

**Queue position:**
- Parent queue: direct subissue of #<parent-issue-number>
- Execution wave: W2
- Ready to start when: Design review for onboarding UI changes is closed

**User stories covered:** Not explicit in source

**Files likely touched:**
- `src/onboarding/`
- `src/ui/`
- `src/integrations/slack/`
- `tests/onboarding/`

**Estimated scope:** Medium: 3-5 files

---

### 4. Implement first project setup step in onboarding

**Parent:** #<parent-issue-number>

**What to build:**
Implement the onboarding step that guides a new admin through completing the first project setup.

**Type:** AFK

**Acceptance criteria:**
- [ ] Admins are guided to complete first project setup during onboarding
- [ ] Project is created and visible in workspace
- [ ] UI and backend changes are coordinated

**Verification:**
- [ ] Tests pass: `<test command>`
- [ ] Build succeeds: `<build command>`
- [ ] Manual check: First project setup flow works end-to-end

**Blocked by:** Design review for onboarding UI changes

**Queue position:**
- Parent queue: direct subissue of #<parent-issue-number>
- Execution wave: W2
- Ready to start when: Design review for onboarding UI changes is closed

**User stories covered:** Not explicit in source

**Files likely touched:**
- `src/onboarding/`
- `src/ui/`
- `src/projects/`
- `tests/onboarding/`

**Estimated scope:** Medium: 3-5 files

---

## Summary

Created task graph for workspace onboarding features.

Parent: #<parent-issue-number> Workspace Onboarding: Invite Teammates, Connect Slack, Complete First Project Setup

Child issues:
1. #<child-issue-number-1> Design review for onboarding UI changes - W1 - HITL - blocked by none
2. #<child-issue-number-2> Implement teammate invitation step in onboarding - W2 - AFK - blocked by #<child-issue-number-1>
3. #<child-issue-number-3> Implement Slack connection step in onboarding - W2 - AFK - blocked by #<child-issue-number-1>
4. #<child-issue-number-4> Implement first project setup step in onboarding - W2 - AFK - blocked by #<child-issue-number-1>

How to grab work:
- Open parent #<parent-issue-number> and inspect its direct subissues.
- Pick the lowest-numbered open AFK wave whose blockers are all closed.
- If the parent issue already existed, read the managed `Task graph` / `How to grab work` section in its body.

Notes:
- All issue numbers and references are placeholders for this dry-run benchmark.
- No GitHub mutation or implementation was performed.
