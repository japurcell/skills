# Output Note

Recommended save path: `/home/adam/.agents/skills/benchmark-triage/SKILL.md`

Invocation command: `/benchmark-triage $benchmark_path`

Assumptions:

- `$benchmark_path` can point to either a `benchmark.json` file or an iteration directory containing that file.
- The benchmark lives beside eval directories and run artifacts that can be inspected during per-eval deep dives.
- The workflow should run as a forked, self-contained analysis and may use task agents plus small local Python helpers when useful.
