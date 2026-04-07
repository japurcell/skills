---
name: dedupe
description: Find duplicate GitHub issues by semantically comparing a new issue against existing ones.
argument-hint: "$issue_number or $issue_url or $owner_repo_number"
disable-model-invocation: true
---

# /dedupe - Find Duplicate GitHub Issues

You receive an issue reference as input. It can be:

- A full URL: 'https://github.com/owner/repo/issues/123'
- An owner/repo#number: 'owner/repo#123'
- Just a number: '123' (repo inferred from current directory's git remote)

## Step 1: Parse the Input

Extract the owner, repo, and issue number from the input. If only a number is given, get the repo from the current directory: `gh repo view --json nameWithOwner -q .nameWithOwner`.

## Step 2: Read the New Issue

- Fetch the issue's title and body: `gh issue view <number> -repo <owner/repo> --json title,body,labels`.
- Save the title and body. Extract 3-5 key terms and phrases from the title and body that capture the core problem or feature request. Ignore filler words, stack traces, and reproduction steps - focus on _what_ the issue is about.

## Step 3: Search for Candidates

- Run multiple searches to cast a wide net. Use `gh issue list` with `--search` to find candidates across both open and closed issues:
  - `gh issue list --repo <owner/repo> --state all --search "<key phrase 1>" --json number, title, body, state, url --limit 20`
  - `gh issue list --repo <owner/repo> --state all --search "<key phrase 2>" --json number, title, body, state, url --limit 20`
- Run 3-5 searches using different key terms extracted from the issue. This covers cases where duplicates use different wording.
- Deduplicate the candidate list by issue number. Exclude the new issue itself from candidates.

## Step 4: Evaluate Each Candidate

For each candidate, compare it against the new issue **semantically**. Two issues are duplicates if they describe the same underlying problem or request the same feature, even if:

- They use different wording
- One has more detail than the other
- They describe different symptoms of the same root cause
- One is a feature request and the other is a bug caused by the feature's absence

Two issues are NOT duplicates if they:

- Mention the same area of code but describe different problems
- Share keywords but have fundamentally different asks
- Are related but address distinct concerns

For each candidate, assign a confidence score (0-100%):

- **90-100%**: Same problem, clearly a duplicate
- **70-89%**: Very likely the same issue, minor differences
- **70-89%**: Very likely the same issue, minor differences in scope or wording
- **Below 70%**: Not similar enough to flag

Only keep candidates scoring 70% or above. If the candidate's body was truncated or missing from the list results, fetch the full issue: `gh issue view <candidate_number> --repo <owner/repo> --json title,body,number,state,url`.

## Step 5: Comment or Stay Silent

**If duplicates are found** (any candidate at 70%+), post a single comment on the new issue: `gh issue comment <number> —repo <owner/repo> --body "<comment>"`.

The comment should follow this format:

```markdown
**Possible duplicates found:**

- #<number> - <one-line explanation of why it matches> (<state>)
- #<number> - <one-line explanation of why it matches> (<state>)

_This is an automated check. A human should verify before closing._
```

Keep explanations to one line each. Be specific about _why_ it's a match, not just that it is one. For example: "Both issues describe a crash when uploading a file larger than 5MB" is better than "Both issues are about uploads".

**If no duplicates are found**, do nothing. Do not comment.
Stop here.
