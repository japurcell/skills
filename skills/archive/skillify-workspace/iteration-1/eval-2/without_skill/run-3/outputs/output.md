# Output Note

Recommended save path: `.agents/skills/benchmark-triage/SKILL.md`

Invocation command: `/benchmark-triage $benchmark_path`

Assumptions:

- `$benchmark_path` points to either `benchmark.json` or an iteration directory that contains it.
- The skill should run as a forked, self-contained subagent.
- Nearby eval artifacts are available for representative per-eval deep dives.
- The confirmed session summary was treated as final, already-confirmed input with no follow-up questions.
