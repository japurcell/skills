# Output Note

Recommended save path: `.agents/skills/ship-hotfix/SKILL.md`

Invocation command:

```text
/ship-hotfix $pr_number $target_environment
```

Assumptions:

- The source pull request already exists and has been reviewed.
- The repository has an established release branch naming rule and a known base branch for hotfix releases.
- The agent should prefer `gh` CLI and `git` over browser-driven GitHub steps.
- Merge and deployment require explicit human approval and must not happen automatically.
- The expected deliverables are the merged release PR URL, deployment outcome, and a Slack-ready summary.
