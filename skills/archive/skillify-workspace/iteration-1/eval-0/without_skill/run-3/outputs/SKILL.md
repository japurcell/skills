# ship-hotfix

## Purpose

Use this skill to ship an already-reviewed hotfix from an existing pull request onto the release branch, stop for explicit human approval before irreversible actions, and finish with a merged release PR URL, deployment status, and a Slack-ready release summary.

## When To Use

- The hotfix code has already been reviewed in an existing pull request.
- A release branch must be created or updated from the correct base branch.
- The hotfix must be cherry-picked onto that release branch.
- The workflow must use `gh` CLI and `git`, not browser-only GitHub steps.
- Merge and deployment require an explicit human checkpoint.

## Invocation

`/ship-hotfix $pr_number $target_environment`

## Arguments

- `$pr_number`: pull request number for the already-reviewed hotfix.
- `$target_environment`: optional environment label such as `staging` or `production`.

## Required Inputs

- The already-open source pull request number.
- The repository's release branch naming and base branch rules.
- The target environment if deployment is environment-specific.

## Success Criteria

- The release branch is created from the correct base branch.
- The reviewed hotfix commit(s) are cherry-picked cleanly onto the release branch.
- Smoke tests pass and CI is green before merge.
- No merge or deployment happens without explicit human approval.
- The final response includes the release PR URL, deployment outcome, and a Slack-ready summary block.

## Tooling

- `Bash(git:*)`
- `Bash(gh:*)`
- `Read`
- `Edit`
- `Write`

## Workflow

1. Inspect the source pull request with `gh` and collect the commit SHAs, linked issue, title, branch details, and current CI status.
2. Identify the correct release base branch and derive the release branch name using the repository's naming rules.
3. Create the release branch from the correct base if it does not exist, or update it safely if it already exists.
4. Cherry-pick the reviewed hotfix commit(s) onto the release branch and resolve conflicts carefully if they occur.
5. Run the repository's smoke tests and any lightweight validation needed before opening or updating the release pull request.
6. Open or update the release pull request with a concise summary that references the source pull request, the linked issue, and the target environment when provided.
7. Check CI for the release pull request and do not proceed until required checks are green.
8. Pause and ask for explicit human approval before merge and before deployment. Treat both as irreversible checkpoints.
9. After approval, merge the release pull request using `gh` or the repository's approved CLI flow.
10. Trigger or confirm deployment using the repository's standard CLI-safe process.
11. Report the merged release pull request URL, deployment result, and a Slack-ready summary block.

## Operating Rules

- Prefer `gh` CLI and `git` for repository operations.
- Do not switch to browser-driven instructions unless the repository workflow explicitly requires it and the user approves.
- Record tool use narrowly and concretely.
- Treat merge and deployment as human-gated actions.
- If CI is failing, the cherry-pick does not apply cleanly, or the base branch is unclear, stop and surface the blocker before proceeding.

## Final Output Format

Provide:

- The merged release pull request URL.
- The deployment status or blocker.
- A Slack-ready summary block that includes the hotfix PR reference, release PR link, environment, and outcome.

Example summary block:

```text
Hotfix shipped
Source PR: #123
Release PR: https://github.com/org/repo/pull/456
Environment: production
Deployment: succeeded
Notes: Cherry-picked reviewed hotfix and merged after green CI and explicit approval.
```
