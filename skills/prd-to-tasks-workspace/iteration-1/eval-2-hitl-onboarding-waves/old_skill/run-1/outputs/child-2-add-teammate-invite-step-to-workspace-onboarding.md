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
