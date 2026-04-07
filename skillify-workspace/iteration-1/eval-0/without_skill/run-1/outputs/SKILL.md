---
name: ship-hotfix
description: Ship an already-reviewed hotfix from an existing pull request to the release branch, with explicit human approval before merge and deploy.
---

# Ship Hotfix

You are a code agent helping ship a reviewed hotfix from an existing pull request to the release branch.

Prefer `gh` CLI and `git` for GitHub and branch operations. Do not switch to browser-style instructions unless the repository workflow makes CLI execution impossible.

## When To Use

Use this skill when:

- The hotfix work already exists in an open, reviewed pull request.
- You need to move the approved change onto a release branch.
- The user wants a controlled release workflow with a human checkpoint before any irreversible action.

Do not use this skill for building a hotfix from scratch or for speculative release planning.

## Invocation

Use:

```text
/ship-hotfix $pr_number $target_environment
```

Arguments:

- `$pr_number`: pull request number for the already-reviewed hotfix.
- `$target_environment`: optional environment label such as `staging` or `production`.

## Inputs

Gather or confirm the following before acting:

- The already-open source pull request.
- The repository's release branch naming rules.
- The correct base branch for the release branch.
- The target environment, if deployment is expected.

## Success Criteria

The task is successful only if all of the following are true:

- The release branch is created from the correct base.
- The reviewed hotfix commit(s) are applied to the release branch.
- Smoke tests and CI are green before merge.
- No merge happens without explicit human approval.
- No deployment happens without explicit human approval.
- The final response includes the merged release PR URL.
- The final response includes the deployment outcome.
- The final response includes a Slack-ready summary block.

## Tooling Expectations

Prefer these tools:

- `Bash(git:*)`
- `Bash(gh:*)`
- `Read`
- `Edit`
- `Write`

No subagent is required for the standard flow.

## Guardrails

- Use `gh` CLI and `git` as the default path for inspection, PR updates, merge operations, and status checks.
- Record permissions and tool usage narrowly. Do not describe capabilities more broadly than needed.
- Treat merge and deployment as irreversible actions that require an explicit user checkpoint.
- If CI is failing, stop and report the failure instead of forcing the release forward.
- If the source PR contains multiple candidate commits, identify the exact commit SHAs before cherry-picking.
- If the base branch or release naming rule is unclear from repository context, stop and surface the ambiguity before creating the release branch.

## Workflow

1. Inspect the source PR.
   - Read the PR summary, linked issue, commit list, and current CI state.
   - Capture the reviewed hotfix commit SHA or SHAs that must be released.

2. Prepare the release branch.
   - Determine the correct base branch using the repository's release rules.
   - Create the release branch from that base, or update the existing release branch if one already exists for this hotfix.

3. Apply the hotfix.
   - Cherry-pick the reviewed hotfix commit or commits onto the release branch.
   - Resolve conflicts carefully and verify that only the intended changes are included.

4. Validate the branch.
   - Run the repository's smoke tests.
   - Push the branch and verify CI status.
   - Do not proceed to merge while tests or CI are failing.

5. Open or update the release PR.
   - Create or refresh the release PR using a concise description of the hotfix, linked issue, and validation status.
   - Keep the PR text short and operationally useful.

6. Pause for explicit approval.
   - Present the release PR link, branch details, CI status, and deployment target.
   - Ask for explicit approval before merge.
   - Ask for explicit approval before deployment if deployment is a separate step.

7. Merge and deploy after approval.
   - Merge the release PR only after the human checkpoint is satisfied.
   - Trigger the deployment using the repository's normal release path.
   - Monitor deployment status until a clear outcome is available.

8. Deliver the final release summary.
   - Return the merged release PR URL.
   - Return the deployment status or deployed environment result.
   - Return a Slack-ready summary block that can be pasted without rewriting.

## Final Response Format

Include these three parts:

1. Release PR URL.
2. Deployment outcome.
3. Slack-ready summary.

Example structure:

```text
Release PR: <url>
Deployment: <status>

Slack summary:
Hotfix shipped from PR #<number> to <environment>.
Release PR: <url>
Deploy status: <status>
Linked issue: <issue or none>
```
