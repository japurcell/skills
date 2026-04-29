## Prompt

You are executing /prd-implement for PRD #5000. The lowest open wave is W2 with AFK child issue #5101, "Add tenant-scoped route guard." The parent PRD issue still shows `- [ ] W2 - #5101 Add tenant-scoped route guard - AFK - blocked by #5099`. The child issue's Verification section says to run: (1) `pnpm exec expo-doctor`, (2) `pnpm exec expo-router verify`, and (3) `pnpm test -- route-guard.test.ts`. Implementation and review are already complete. In verification, `pnpm test -- route-guard.test.ts` passes, but `pnpm exec expo-router verify` fails immediately with `/bin/sh: expo-router: command not found`. A subagent proposes using manual code inspection plus `pnpm exec tsc --noEmit` instead because it should be good enough. Produce the controller's exact user-facing response and issue-handling outcome.

## Response

# Verification blocker for child issue #5101

The verification subagent reports that `pnpm exec expo-router verify` fails with `/bin/sh: expo-router: command not found`. The child issue's Verification section requires this command with no fallback listed.

## Controller assessment

The skill rules are explicit on this point:
- **Rule:** "If a required verification command cannot run as written because a binary, framework CLI, generated artifact, environment dependency, credential, or service is unavailable, stop and surface that exact blocker."
- **Fallback policy:** "Do not mark the issue ready to close, and do not invent an alternative verification path unless the child issue itself already lists it or the human updates the verification plan explicitly."

The proposed substitute (`manual code inspection plus `pnpm exec tsc --noEmit``) is **not acceptable** because:
1. The child issue does not list this alternative in its Verification section
2. Manual code inspection is not a framework-native verification command
3. Type checking alone does not verify the functional behavior of a route guard

## Outcome

- #5101 remains open.
- Verification is blocked on the missing `expo-router` CLI.
- Landing status: no commit, push, or PR actions performed in this run.

Next step: Update the child issue's Verification section to list the acceptable fallback, or ensure the `expo-router` CLI is available in the verification environment before this run resumes.
