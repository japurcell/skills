---
name: gh-attach-subissue
description: Attaches a GitHub child issue as a true sub-issue of a parent issue with `gh` and GitHub GraphQL. Use whenever the user wants to make one issue a child of another, attach a task under a parent issue, build an issue tree, or asks for the `addSubIssue` mutation or exact `gh api graphql` command shape. Use this even if they only say "make #123 a child of #45" or "link this issue under the tracker" and they need a real GitHub sub-issue rather than a plain text reference.
---

# gh-attach-subissue

## Overview

Create real GitHub sub-issue relationships by resolving both issues to node IDs and calling the GraphQL `addSubIssue` mutation through `gh api graphql`.

The key safety rule is simple: inline the resolved node IDs directly into the mutation text. Do not write shell commands that embed GraphQL `$variables` such as `mutation($parentId: ID!, ...)`, because those tokens can look like suspicious shell expansion and get blocked before the command ever runs.

## When to Use

- The user wants a true GitHub sub-issue relationship between two existing issues.
- The user mentions a parent issue, child issue, sub-issue, issue tree, tracker issue, or asks to attach one issue under another.
- The user asks for the exact `gh api graphql` command or the `addSubIssue` mutation shape.
- The user explicitly wants GitHub-native hierarchy rather than a loose body reference.
- Do **not** use this skill for ordinary issue cross-links, closing keywords, or a plain `Parent: #123` note unless a real sub-issue attach is unavailable and the user accepts that fallback.

## Workflow

1. Confirm the repository and both issue numbers.
   - Accept any of these inputs: `owner/repo#123`, full issue URLs, or issue numbers when the repo context is already known.
   - If either repo context or an issue number is missing, stop and ask instead of guessing.

2. Resolve the parent and child node IDs.
   - `addSubIssue` needs GraphQL node IDs, not issue numbers.
   - Use `gh api repos/<owner>/<repo>/issues/<number> --jq .node_id` for both issues.
   - Treat an empty value or API error as a hard failure.

```bash
PARENT_NODE_ID=$(gh api repos/OWNER/REPO/issues/PARENT_NUMBER --jq .node_id)
CHILD_NODE_ID=$(gh api repos/OWNER/REPO/issues/CHILD_NUMBER --jq .node_id)
```

3. Run the GraphQL mutation with the resolved IDs inlined into the query text.
   - Keep the query shell-safe by embedding the resolved IDs directly in the mutation body.
   - Do **not** use GraphQL variables such as `mutation($parentId: ID!, $childId: ID!)` together with `-F parentId=...`.
   - If you already know the literal node IDs, substitute them directly.

```bash
gh api graphql -f query="mutation { addSubIssue(input: {issueId: \"$PARENT_NODE_ID\", subIssueId: \"$CHILD_NODE_ID\"}) { issue { number } } }"
```

4. Report the result honestly.
   - Success means the mutation returned data without GraphQL errors.
   - If the command fails, surface the exact error and say the sub-issue link was **not** created.
   - When giving the user a reusable snippet, prefer the exact command shape above over pseudo-code.

5. Use fallback language carefully.
   - A body line like `Parent: #123` is only a textual convention; it does **not** create a real GitHub sub-issue.
   - Only mention that fallback when the platform or repo does not support sub-issues and the user still wants a weaker alternative.
   - Label that fallback explicitly as non-equivalent.

## Command Template

Use this flow when you need a complete, reproducible shell sequence:

```bash
OWNER=acme
REPO=platform
PARENT_NUMBER=42
CHILD_NUMBER=128

PARENT_NODE_ID=$(gh api repos/$OWNER/$REPO/issues/$PARENT_NUMBER --jq .node_id)
CHILD_NODE_ID=$(gh api repos/$OWNER/$REPO/issues/$CHILD_NUMBER --jq .node_id)

gh api graphql -f query="mutation { addSubIssue(input: {issueId: \"$PARENT_NODE_ID\", subIssueId: \"$CHILD_NODE_ID\"}) { issue { number } } }"
```

If the user asks for the final command only, show the mutation command and keep the node-ID lookup commands alongside it unless the IDs are already known.

## Response Shape

When you answer, keep the output concrete:

1. Name the parent and child issues you are linking.
2. Show the node-ID lookup commands or state the resolved node IDs if you already have them.
3. Show the exact `gh api graphql` mutation command.
4. End with either a success statement or the exact failure condition.

## Common Rationalizations

| Rationalization | Reality |
| --- | --- |
| "The issue numbers should be enough." | `addSubIssue` requires GraphQL node IDs, not `#123` style issue numbers. |
| "I'll use GraphQL variables like `$parentId` to keep the query tidy." | Inside a shell command, those `$...` tokens can be flagged as suspicious expansion. Inline the resolved IDs in the query text instead. |
| "A `Parent: #123` line is basically the same thing." | It is not a true GitHub sub-issue relationship and should never be presented as equivalent. |
| "If the mutation looks right, I can say it worked." | Only claim success when the command actually returns success data without errors. |

## Red Flags

- The mutation text contains `mutation($parentId:` or other GraphQL variable declarations.
- The command passes issue numbers where node IDs belong.
- The answer silently swaps in a body reference instead of a real sub-issue attach.
- The result claims success without showing or describing the actual mutation outcome.

## Verification

After completing the workflow, confirm:

- [ ] Repository context, parent issue, and child issue are explicit.
- [ ] Both issue node IDs were resolved before calling `addSubIssue`.
- [ ] The GraphQL mutation text inlines resolved IDs and does not declare GraphQL `$variables`.
- [ ] The final response clearly states whether the true sub-issue link was created.
- [ ] Any fallback is labeled as a weaker non-equivalent alternative.
