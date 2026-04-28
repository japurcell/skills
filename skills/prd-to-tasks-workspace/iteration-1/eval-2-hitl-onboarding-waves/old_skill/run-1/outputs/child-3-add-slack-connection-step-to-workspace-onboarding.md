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
