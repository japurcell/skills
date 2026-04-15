# Benchmark Output Note

Recommended save path: `.agents/skills/ship-hotfix/SKILL.md`

Invocation command: `/ship-hotfix $pr_number $target_environment`

Assumptions:

- The source pull request is already open and already reviewed.
- The repository has an established release base branch and release branch naming convention.
- The repository exposes smoke tests, CI checks, and a deployment mechanism the agent can invoke or verify.
- Merge and deployment require an explicit human checkpoint.
- `gh` CLI and `git` are the preferred interfaces for the workflow.
