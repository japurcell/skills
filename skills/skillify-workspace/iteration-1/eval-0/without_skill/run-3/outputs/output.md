Recommended save path: `.agents/skills/ship-hotfix/SKILL.md`

Invocation command: `/ship-hotfix $pr_number $target_environment`

Assumptions:

- The confirmed session summary in `repo-hotfix-release.md` is authoritative and already reflects user-approved answers.
- The workflow is repository-specific and should not be framed as a personal habit or generic release guide.
- Merge and deployment remain human-gated actions that require explicit approval at execution time.
- The repository has an established release branch naming rule, smoke-test command, and deployment path that the agent can inspect when the skill is used.
