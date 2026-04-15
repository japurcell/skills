Recommended save path: `.agents/skills/benchmark-triage/SKILL.md`

Invocation command: `/benchmark-triage $benchmark_path`

Assumptions:

- The confirmed session summary in `forked-benchmark-triage.md` is authoritative and replaces the normal interview rounds.
- The skill should run as a forked, self-contained workflow.
- `$benchmark_path` may point either to a `benchmark.json` file or to an iteration directory that contains benchmark outputs.
- The tool mix should stay narrow to benchmark analysis, including local Python helpers and Task agents for parallel per-eval review when useful.
