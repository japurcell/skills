---
name: ship-hotfix
description: Ship an already-reviewed hotfix PR onto the release branch, require explicit approval before merge and deployment, and finish with a Slack-ready release summary.
allowed-tools:
  - Bash(git:*)
  - Bash(gh:*)
  - Read
  - Edit
  - Write
argument-hint: "<pr_number> [target_environment]"
arguments:
  - pr_number
  - target_environment
when_to_use: Use when you need to ship an already-reviewed hotfix from an existing pull request to the repo's release branch, want the workflow driven through `gh` CLI and `git`, and need an explicit approval checkpoint before merge or deployment. Trigger phrases: "ship hotfix", "release this hotfix PR", "cut a hotfix release from PR", or "promote reviewed hotfix".
---

# Ship Hotfix

Release a reviewed hotfix from an existing pull request onto the correct release branch, verify it is safe to ship, pause for approval before irreversible actions, then return the merged release PR URL, deployment outcome, and a Slack-ready summary.

## Inputs

- `$pr_number`: Pull request number for the already-reviewed hotfix.
- `$target_environment`: Optional environment label such as `staging` or `production`.

## Goal

Create or update the correct release branch from the proper base, cherry-pick the reviewed hotfix commit(s), verify smoke tests and CI are green, open or update the release PR, require explicit user approval before merge and deployment, and finish with the merged release PR URL, deployment status, and a paste-ready release summary.

## Steps

### 1. Inspect the source PR

Use `gh pr view $pr_number` and related `gh` queries to collect the source PR title, URL, linked issue, commit SHAs, base branch, review state, and current CI status. Confirm this is the already-reviewed hotfix that should be promoted and identify the correct release base branch using the repo's naming rules.

**Success criteria**:

- The source PR URL, commit SHA list, linked issue, and current CI state are captured.
- The correct release base branch is identified before any branch creation begins.

**Artifacts**: Source PR URL, commit SHAs, linked issue, release base branch.

**Rules**:

- Prefer `gh` CLI and `git`; do not switch to browser-only instructions.
- Do not assume the release base branch; verify it from repo rules or branch conventions.

### 2. Create or update the release branch

Fetch the latest refs, then create or refresh the release branch from the verified base branch using the repo's branch naming rules. If the release branch already exists, update it instead of creating a duplicate branch.

**Success criteria**:

- The release branch exists locally from the correct base branch.
- The branch name matches repo conventions and is ready for cherry-picks.

**Artifacts**: Release branch name.

**Rules**:

- The release branch must originate from the verified base branch.
- Do not continue if the branch base is ambiguous.

### 3. Cherry-pick the reviewed hotfix commits

Cherry-pick the reviewed hotfix commit(s) from the source PR onto the release branch in order. Resolve conflicts carefully, verify the resulting diff only contains intended hotfix changes, then push the branch.

**Success criteria**:

- All intended hotfix commits are applied to the release branch in the right order.
- Any conflicts are resolved and the branch pushes successfully.

**Rules**:

- Cherry-pick only the reviewed hotfix commit(s); do not pull in unrelated changes.
- Stop and surface conflicts clearly if they cannot be resolved safely.

### 4. Validate smoke tests and CI

Run the repo's expected smoke tests for the release branch and confirm the required CI checks for the release branch or release PR are green. Record anything unusual that a reviewer should know.

**Success criteria**:

- Required smoke tests complete successfully or their outcome is explicitly documented.
- Required CI checks are green before merge is considered.

**Artifacts**: Smoke test outcome, CI status.

**Rules**:

- Do not proceed to merge or deployment while CI is failing, pending, or unknown.

### 5. Open or update the release PR

Use `gh` CLI to create or update the release PR with a concise summary of the hotfix, linked issue, cherry-picked commits, and target environment if one was provided.

**Success criteria**:

- A release PR exists for the branch.
- The PR description is concise and includes the information reviewers need.

**Artifacts**: Release PR URL.

**Rules**:

- Reuse the existing release PR when appropriate instead of opening duplicates.
- Keep the summary concise and operationally useful.

### 6. Approval checkpoint [human]

Present the release PR URL, cherry-picked commit list, CI status, and intended target environment, then pause for explicit approval before any merge or deployment action.

**Success criteria**:

- Explicit user approval is received before continuing.
- If approval is not granted, the workflow stops with the current status summarized.

**Human checkpoint**: Required before merge and deployment.

**Rules**:

- No merge happens without explicit approval.
- No deployment happens without explicit approval.

### 7. Merge the release PR and trigger deployment

After approval and green CI, merge the release PR using the repo's standard merge method and trigger the deployment using the repo's standard deployment mechanism for `$target_environment` when provided.

**Success criteria**:

- The release PR is merged.
- Deployment is triggered or completed, and its current outcome is captured.

**Artifacts**: Merged release PR URL, deployment status.

**Rules**:

- This is irreversible; do not proceed without the human checkpoint.
- If CI changes from green to failing, stop and re-evaluate before merging.

### 8. Return the release summary

Prepare a Slack-ready summary block that includes the source PR, merged release PR URL, linked issue, target environment, and deployment outcome.

**Success criteria**:

- The final output includes the merged release PR URL.
- The final output includes the deployment outcome.
- The final output includes a paste-ready Slack summary.
