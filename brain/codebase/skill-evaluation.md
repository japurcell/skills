# Skill evaluation caveats

- Inspect `summary.failed`; a grader may exit 0 while reporting failed cases.
- Keep baseline/input fixtures immutable. Separate actual measurements from proxy values and absent data.
- `quick_validate.py` accepts the documented `disable-model-invocation` field. Preserve explicit-only invocation controls; do not remove them to silence tooling.
- Current `aggregate_benchmark.py` substitutes output character count when token count is absent, and zero when duration is absent. These are not measured tokens or time.
- Use canonical benchmark iteration layouts and the affected skill's public grader commands.
- Do not retain deleted-feature evaluation suites as ongoing requirements.

Invocation-control source: [official Claude Code skill reference](https://code.claude.com/docs/en/skills#frontmatter-reference), checked 2026-10-20. Harness support can differ; AGENTS.md also explicitly limits meditate/ruminate invocation.

Evidence: current skill tooling and `scripts/test_helpers.py`, checked 2026-10-20 during migration inventory. Recheck validator allowlists, aggregate schema, and benchmark tooling before relying on metrics.
