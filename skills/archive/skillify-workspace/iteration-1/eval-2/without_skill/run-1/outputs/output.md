Recommended save path: `.agents/skills/benchmark-triage/SKILL.md`

Invocation command: `/benchmark-triage $benchmark_path`

Assumptions:

- The benchmark input is either a `benchmark.json` file or an iteration directory containing one.
- The skill should run as a forked, self-contained subagent with no follow-up questions once the benchmark path is known.
- Nearby eval artifacts such as transcripts, outputs, and prompts are available for representative deep dives.
- The final deliverable from the skill is a short triage report that clusters failures, flags flaky assertions, and recommends concrete next edits.
