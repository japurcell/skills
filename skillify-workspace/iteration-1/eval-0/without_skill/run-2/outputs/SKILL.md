---
name: ship-hotfix
description: Create or update a release branch from an already-reviewed hotfix PR, pause for explicit approval before merge and deploy, and return the release PR URL, deployment status, and a Slack-ready summary.
---

# Ship Hotfix

Use this skill when a reviewed hotfix already exists in a pull request and the goal is to promote it onto the correct release branch, verify it, and ship it with an explicit human checkpoint before any irreversible action.

## Invocation

`/ship-hotfix $pr_number $target_environment`

Arguments:

- `$pr_number`: pull request number for the already-reviewed hotfix.
- `$target_environment`: optional environment label such as `staging` or `production`.

## Required Inputs

Before executing the workflow, confirm or discover:

- The source hotfix pull request.
- The correct release base branch.
- The repository's release branch naming rules.
- The deployment target or environment, if one was supplied.

If a required repo-specific detail is missing and cannot be derived from the repository, stop and ask for it before making changes.

## Tooling And Permissions

Prefer command-line workflows over browser instructions.

- `Bash(git:*)`
- `Bash(gh:*)`
- `Read`
- `Edit`
- `Write`

Do not broaden permissions unless the repository clearly requires more.

## Success Criteria

The workflow is only complete when all of the following are true:

- The release branch was created from the correct base.
- Only the reviewed hotfix commit set was applied.
- Smoke tests and CI are green before merge.
- No merge or deployment happened without an explicit human checkpoint.
- The final response includes the release PR URL and deployment outcome.

## Workflow

1. Inspect the source PR with `gh pr view` and collect the commit SHAs, linked issue, branch information, reviewers, and current check status.
2. Verify the PR is already reviewed and identify the exact hotfix commit set to promote.
3. Determine the correct release base branch and compute the release branch name according to repository rules.
4. Create the release branch from the correct base, or update it if it already exists.
5. Cherry-pick the reviewed hotfix commit(s) onto the release branch. Resolve conflicts carefully and stop if the intended commit set becomes ambiguous.
6. Run the repository's smoke tests or other lightweight release validation.
7. Push the release branch and open or update the release PR with a concise summary that links back to the source PR and issue.
8. Check PR status and CI with `gh pr checks` or equivalent until the release PR is ready for human review.
9. Present a checkpoint summary and stop for explicit approval before merge or deployment.
10. After approval, merge the release PR using the repository's normal release method.
11. Trigger or confirm deployment for the target environment.
12. Publish a final summary that includes the merged release PR URL, deployment status, and a Slack-ready release note block.

## Mandatory Human Checkpoint

Before merge or deployment, stop and present:

- Source PR number and title.
- Release branch name.
- Release PR URL.
- Current CI or smoke-test status.
- Target environment.
- The exact next irreversible actions.

Do not merge. Do not deploy. Wait for explicit approval.

## Command Guidance

Prefer patterns like these, adapted to the repository:

```bash
gh pr view "$pr_number" --json number,title,body,headRefName,baseRefName,commits,reviewDecision,statusCheckRollup
git fetch --all --prune
git checkout -B "$release_branch" "origin/$release_base"
git cherry-pick <commit_sha>
gh pr create --base "$release_base" --head "$release_branch" --title "$release_title" --body "$release_body"
gh pr checks "$release_pr_number" --watch
gh pr merge "$release_pr_number" --merge
```

Use repository-specific commands for testing and deployment. If the repository has an existing release script or documented flow, prefer that over inventing a new one.

## Guardrails

- Prefer `gh` CLI and `git`; do not switch to browser-only instructions unless explicitly requested.
- Keep the workflow inline. Do not hide approval steps inside automation.
- Do not merge unrelated commits into the release branch.
- Do not proceed if the release base branch is uncertain.
- Do not proceed if CI is failing, unless the human explicitly approves an exception.
- Do not deploy before the release PR is merged and approved.

## Final Output

Return a concise summary containing:

- Merged release PR URL.
- Deployment status and target environment.
- Any manual follow-up still required.
- A Slack-ready summary block.

Example Slack-ready block:

```text
Hotfix shipped
- Source PR: #123
- Release PR: https://github.com/org/repo/pull/456
- Environment: production
- Status: deployed successfully
- Summary: Cherry-picked reviewed hotfix for <issue/customer impact>
```
