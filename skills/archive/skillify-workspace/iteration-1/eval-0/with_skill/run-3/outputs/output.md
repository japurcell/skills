Recommended save path: `.agents/skills/ship-hotfix/SKILL.md`

Invocation command: `/ship-hotfix $pr_number [$target_environment]`

Assumptions:

- The source pull request is already reviewed and ready to release.
- The repository has established release branch naming and base-branch rules that the operator can determine during step 1.
- The repository has a known smoke-test or minimal validation command, but the exact command is intentionally left repo-specific.
- `gh` CLI authentication and git remote access are already configured.
- Merge and deployment require explicit human approval because the workflow stays inline.
