---
name: commit-to-pr
description: Given the current git status, create a new branch (if on main), commit the changes, push the branch to origin, and create a pull request using `gh pr create`.
disable-model-invocation: true
---

# Commit to PR

## Inputs

You receive these parameters in your prompt:

- **spec_file** (required): The path to the spec file that contains the linked Github issue.

## Context

- Current git status: !`git status`
- Current git diff (staged and unstaged changes): !`git diff HEAD`
- Current branch: !`git branch --show-current`

## Your task

Based on the above changes:

1. Read spec_file into context if it isn't already
1. Create a new branch <feature-name>
1. Create a single commit with an appropriate message ensuring:
   - The commit is atomic and follows best practices (e.g. conventional commits)
   - The commit is linked to any relevant issue numbers (e.g. "Fixes #<linked issue number>")
1. Push the branch to origin
1. Create a pull request using `gh pr create` ensuring that the pull request is linked to any relevant issue numbers.
1. You have the capability to call multiple tools in a single response. You MUST do all of the above in a single message. Do not use any other tools or do anything else. Do not send any other text or messages besides these tool calls.
