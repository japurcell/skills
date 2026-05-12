# Confirmed Session Summary: ship-hotfix

## What Happened

- The user asked to turn a just-finished production hotfix session into a reusable skill.
- The goal was a repo-specific workflow for shipping a reviewed hotfix from an existing pull request to the release branch.
- The session ended when the agent had a merged release PR URL and a short release-note summary ready to paste into Slack.

## Confirmed Answers

- Confirmed skill name: `ship-hotfix`
- Confirmed save location: `.agents/skills/ship-hotfix/SKILL.md`
- Confirmed invocation style: `/ship-hotfix $pr_number $target_environment`
- Confirmed arguments:
  - `$pr_number`: pull request number for the already-reviewed hotfix
  - `$target_environment`: optional environment label such as `staging` or `production`
- Confirmed context choice: keep this inline because the user wants explicit approval before merge and deploy

## Inputs And Success Criteria

- Inputs: an already-open pull request, target branch naming rules, target environment
- Success artifact: merged release PR URL, deployment status, and a Slack-ready summary block
- Hard success criteria:
  - The release branch is created from the correct base
  - CI is green before merge
  - No merge or deploy happens without a human checkpoint
  - The final output includes the release PR URL and deployment outcome

## Observed Workflow Steps

1. Inspect the source PR and collect the commit SHAs, linked issue, and current CI state.
2. Create or update the release branch from the correct base branch.
3. Cherry-pick the reviewed hotfix commit(s) onto the release branch.
4. Run the repo's smoke tests and check CI.
5. Open or update the release PR with a concise summary.
6. Pause for explicit user approval before merge and deployment.
7. Merge the release PR and trigger the deployment.
8. Post a Slack-ready summary with links to the PR and deploy status.

## User Corrections And Preferences

- The user corrected the agent when it started using browser-style GitHub instructions; the workflow must prefer `gh` CLI and `git`.
- The user wanted tool permissions recorded narrowly rather than generically.
- The user specifically asked for an explicit human checkpoint before any irreversible action.
- The workflow is repo-specific, not personal.

## Tools And Agents Used

- `Bash(git:*)`
- `Bash(gh:*)`
- `Read`
- `Edit`
- `Write`
- No subagent was required in the original session.
