## Parent

#<parent-issue-number>

## What to build

Add an onboarding step that guides a new admin through creating the first project from the workspace onboarding flow, including the step UI, project creation path, and completion state so onboarding can end with a usable first project.

## Type

AFK

## Acceptance criteria

- [ ] The onboarding flow includes a first project setup step with enough guidance for a new admin to complete it.
- [ ] Completing the step creates the first project using the intended project setup path.
- [ ] The onboarding flow shows a completion state once the first project is created or the supported completion path is reached.

## Verification

- [ ] Tests pass: `<targeted test command>`
- [ ] Build succeeds: `<build command, if known>`
- [ ] Manual check: Start workspace onboarding as a new admin, create the first project from onboarding, and confirm the flow ends in a completed state with the project available.

## Blocked by

- Blocked by #<child-1-issue-number>

## User stories covered

Not explicit in source

## Files likely touched

- `src/onboarding/steps/first-project-setup.tsx`
- `src/projects/create-project.ts`
- `tests/onboarding/first-project-setup.test.ts`

## Estimated scope

Medium: 3-5 files
