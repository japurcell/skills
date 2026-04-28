## Proposed vertical-slice breakdown

1. **Title**: Design review and approval for onboarding flow
   **Type**: HITL
   **Execution wave**: W1
   **Blocked by**: None
   **User stories covered**: Get design team approval before UI changes

2. **Title**: Invite teammates step with email
   **Type**: AFK
   **Execution wave**: W2
   **Blocked by**: Slice 1: Design review and approval for onboarding flow
   **User stories covered**: Admins can invite team members during onboarding

3. **Title**: Connect Slack integration step
   **Type**: AFK
   **Execution wave**: W2
   **Blocked by**: Slice 1: Design review and approval for onboarding flow
   **User stories covered**: Admins can connect Slack during onboarding

4. **Title**: First project setup step
   **Type**: AFK
   **Execution wave**: W2
   **Blocked by**: Slice 1: Design review and approval for onboarding flow
   **User stories covered**: Admins can create first project during onboarding

5. **Title**: Onboarding completion tracking and analytics
   **Type**: AFK
   **Execution wave**: W3
   **Blocked by**: Slices 2-4: Individual onboarding steps
   **User stories covered**: Track onboarding completion and identify drop-off points

## Child issue drafts

### Child 1: Design review and approval for onboarding flow

## Parent

#6001

## What to build

Get design team approval on the new onboarding flow layout, copy, interactions, and visual design before starting implementation. This is a gate for subsequent UI work.

## Type

HITL

## Acceptance criteria

- [ ] Design review is scheduled with design lead
- [ ] Design artifacts (wireframes/mockups) are shared with team
- [ ] Design approval is documented and linked to this issue

## Verification

- [ ] Design lead approval recorded in comments
- [ ] No implementation work starts until this is closed

## Blocked by

None - can start immediately

## Queue position

- Parent queue: direct subissue of #6001
- Execution wave: W1
- Ready to start when: this issue has no blockers

## User stories covered

Get design team approval before UI changes

## Files likely touched

- Design artifacts (Figma/design tool)
- Design specs/documentation

## Estimated scope

Small: 1-2 files

### Child 2: Invite teammates step with email

## Parent

#6001

## What to build

During onboarding, admins see a step that lets them invite teammates via email. The step should be accessible early in the flow, collect email addresses, send invitations, and provide feedback on success/failure.

## Type

AFK

## Acceptance criteria

- [ ] Invite step renders in onboarding flow
- [ ] Admins can enter multiple email addresses
- [ ] Invitations are sent and success/errors are displayed
- [ ] Step can be skipped to continue onboarding

## Verification

- [ ] Tests pass: `npm run test -- onboarding.inviteTeam.test.ts`
- [ ] Manual check: Complete invite step, verify emails received
- [ ] Build succeeds: `npm run build`

## Blocked by

- Blocked by #<child-1-issue-number>

## Queue position

- Parent queue: direct subissue of #6001
- Execution wave: W2
- Ready to start when: #6001's design review issue is closed

## User stories covered

Admins can invite team members during onboarding

## Files likely touched

- `src/features/onboarding/InviteTeamStep.tsx`
- `src/api/onboarding.ts`
- `tests/features/onboarding/InviteTeamStep.test.ts`

## Estimated scope

Small: 1-2 files

### Child 3: Connect Slack integration step

## Parent

#6001

## What to build

During onboarding, admins see a step to connect Slack. This step should guide them through OAuth, display connection status, and allow them to skip if not ready.

## Type

AFK

## Acceptance criteria

- [ ] Slack connection step renders in onboarding
- [ ] OAuth flow works and stores connection
- [ ] Connection status is displayed
- [ ] Step can be skipped

## Verification

- [ ] Tests pass: `npm run test -- onboarding.slackConnect.test.ts`
- [ ] Manual check: Connect Slack account via step
- [ ] Build succeeds: `npm run build`

## Blocked by

- Blocked by #<child-1-issue-number>

## Queue position

- Parent queue: direct subissue of #6001
- Execution wave: W2
- Ready to start when: #6001's design review issue is closed

## User stories covered

Admins can connect Slack during onboarding

## Files likely touched

- `src/features/onboarding/SlackConnectStep.tsx`
- `src/services/slackIntegration.ts`
- `tests/features/onboarding/SlackConnectStep.test.ts`

## Estimated scope

Medium: 3-5 files

### Child 4: First project setup step

## Parent

#6001

## What to build

During onboarding, admins see a step to create their first project. This step should collect project name and basic settings, create the project, and allow skipping if preferred.

## Type

AFK

## Acceptance criteria

- [ ] Project creation step renders in onboarding
- [ ] Admins can enter project name and settings
- [ ] Project is created and set as active
- [ ] Step can be skipped

## Verification

- [ ] Tests pass: `npm run test -- onboarding.projectSetup.test.ts`
- [ ] Manual check: Create a project via onboarding step
- [ ] Build succeeds: `npm run build`

## Blocked by

- Blocked by #<child-1-issue-number>

## Queue position

- Parent queue: direct subissue of #6001
- Execution wave: W2
- Ready to start when: #6001's design review issue is closed

## User stories covered

Admins can create first project during onboarding

## Files likely touched

- `src/features/onboarding/ProjectSetupStep.tsx`
- `src/api/projects.ts`
- `tests/features/onboarding/ProjectSetupStep.test.ts`

## Estimated scope

Small: 1-2 files

### Child 5: Onboarding completion tracking and analytics

## Parent

#6001

## What to build

Track when admins complete onboarding steps and record drop-off points. This data helps identify where admins abandon the flow.

## Type

AFK

## Acceptance criteria

- [ ] Step completion is recorded in analytics
- [ ] Drop-off points are trackable
- [ ] Dashboard shows completion rates

## Verification

- [ ] Tests pass: `npm run test -- onboarding.analytics.test.ts`
- [ ] Manual check: Complete onboarding and verify analytics data
- [ ] Build succeeds: `npm run build`

## Blocked by

- Blocked by #<child-2-issue-number>, #<child-3-issue-number>, #<child-4-issue-number>

## Queue position

- Parent queue: direct subissue of #6001
- Execution wave: W3
- Ready to start when: all invite, Slack, and project setup issues are closed

## User stories covered

Track onboarding completion and identify drop-off points

## Files likely touched

- `src/services/analyticsService.ts`
- `src/features/onboarding/OnboardingAnalytics.tsx`
- `tests/services/analyticsService.test.ts`

## Estimated scope

Small: 1-2 files

---

## Summary

Created task graph for workspace onboarding feature.

Parent: #6001 (new)

Child issues:

1. #6002 Design review and approval for onboarding flow - W1 - HITL - blocked by none
2. #6003 Invite teammates step with email - W2 - AFK - blocked by #6002
3. #6004 Connect Slack integration step - W2 - AFK - blocked by #6002
4. #6005 First project setup step - W2 - AFK - blocked by #6002
5. #6006 Onboarding completion tracking and analytics - W3 - AFK - blocked by #6003, #6004, #6005

How to grab work:

- Open parent #6001 and inspect its direct subissues.
- The design review (W1) must complete before implementation steps (W2).
- Pick any open AFK issue in the lowest-numbered wave whose blockers are closed.
- Do not start implementation until design review (W1 HITL) is closed.

Notes:

- Design review is HITL and must complete before UI implementation work
- Implementation steps (invite, Slack, project setup) are AFK and can work in parallel once design is approved
- Analytics tracking is separate and depends on all three onboarding steps
- Each step is a small vertical slice that delivers one independently verifiable behavior
- All steps can be skipped by admins if desired
