---
name: ship-hotfix
description: Ship a reviewed hotfix from an existing PR onto the release branch, pause for approval, then merge, deploy, and produce a Slack-ready summary.
allowed-tools:
  - Bash(git:*)
  - Bash(gh:*)
  - Read
  - Edit
  - Write
argument-hint: "$pr_number [$target_environment]"
arguments:
  - pr_number
  - target_environment
context: inline
when_to_use: Use when the user wants to release an already-reviewed hotfix PR to a release branch, especially for requests like "ship this hotfix," "cut a release PR from PR 123," or "deploy this reviewed fix to production."
---

# Ship Hotfix

Release a reviewed hotfix from an existing pull request by creating or updating the release branch, cherry-picking the approved commit set, verifying CI, pausing for approval before irreversible actions, and finishing with a Slack-ready release summary.

## Inputs

- `$pr_number`: Pull request number for the already-reviewed hotfix.
- `$target_environment`: Optional deployment target such as `staging` or `production`.

## Goal

Produce a merged release PR URL, a recorded deployment outcome, and a concise Slack-ready summary block without merging or deploying until the user explicitly approves those actions.

## Steps

### 1. Inspect the source PR

Use `gh pr view $pr_number` and any needed git inspection commands to collect the source branch, reviewed commit SHAs, linked issue, and current CI status. Confirm the hotfix PR is already reviewed and identify the correct release base branch using the repo's branching rules.

**Artifacts**: Reviewed commit SHA list, linked issue reference, release base branch, source PR URL.

**Rules**: Prefer `gh` CLI and `git` over browser-driven workflows. Do not proceed if the PR is unreviewed, ambiguous, or missing the required base-branch information.

**Success criteria**: You have the exact commit set to ship, the correct release base branch, and the current CI state for the source PR.

### 2. Create or update the release branch

Create the release branch from the confirmed base branch, or update the existing release branch if one already exists for this hotfix. Keep the branch state clean and verify it points at the expected base before applying any changes.

**Artifacts**: Release branch name.

**Rules**: The release branch must be created from the correct base branch. If the existing branch is based on the wrong branch or contains unrelated commits, stop and surface the problem instead of repairing it implicitly.

**Success criteria**: The release branch exists locally and remotely, and its base matches the confirmed branch rule for this release.

### 3. Cherry-pick the reviewed hotfix commits

Cherry-pick only the reviewed hotfix commit SHAs onto the release branch, preserving the intended order. Resolve conflicts carefully and verify the resulting diff matches the expected hotfix scope before continuing.

**Artifacts**: Release branch commit range ready for validation.

**Rules**: Only include the reviewed hotfix commits. Do not add opportunistic fixes or unrelated cleanup. If conflict resolution changes behavior materially, stop and ask for guidance.

**Success criteria**: The release branch contains the intended hotfix changes only, with conflicts resolved and the branch in a clean state.

### 4. Validate locally and confirm CI readiness

Run the repo's smoke tests or other minimal release validation expected for hotfixes, then verify the branch is ready for CI. If the repository already has remote CI checks for the release PR, make sure they are green before merge.

**Rules**: Do not continue with failing smoke tests. Do not merge while CI is red or missing required checks.

**Success criteria**: Local smoke validation passes, and the release branch is ready for or already showing green CI results.

### 5. Open or update the release PR

Create the release PR if it does not exist, or update the existing one with a concise summary that explains the hotfix, links the source PR and issue, and captures the target environment when provided.

**Artifacts**: Release PR URL.

**Rules**: Keep the PR description concise and operationally useful. Reuse an existing release PR when appropriate instead of creating duplicates.

**Success criteria**: There is a release PR with the correct branch mapping, a concise summary, and green or actively running CI attached to it.

### 6. Approval checkpoint [human]

Pause and present the release PR URL, current CI status, and intended deployment target. Ask for explicit approval before any merge or deployment action.

**Human checkpoint**: Required before merge and before deployment if they are separate actions.

**Rules**: No irreversible action happens without explicit approval from the user.

**Success criteria**: The user explicitly approves proceeding with merge and deployment.

### 7. Merge the release PR and trigger deployment

After approval, merge the release PR using the repo's normal release practice and trigger the deployment for `$target_environment` if provided, or for the default production path if not. Track deployment status until there is a clear success or failure result.

**Artifacts**: Merge commit or merged PR state, deployment status link or identifier.

**Rules**: If CI turns red or required checks regress before merge, stop and report that the checkpoint is no longer valid. If deployment fails, capture the failure state and do not claim release success.

**Success criteria**: The release PR is merged, deployment has been triggered, and the deployment outcome is known.

### 8. Produce the release summary

Prepare a Slack-ready summary block that includes the release PR URL, source PR reference, linked issue if available, deployment target, and final deployment outcome.

**Artifacts**: Slack-ready release summary block.

**Success criteria**: The final output includes the merged release PR URL, deployment outcome, and a concise summary ready to paste into Slack.
