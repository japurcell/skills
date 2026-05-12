# Benchmark Run Output

Recommended save path: `.agents/skills/benchmark-triage/SKILL.md`

Invocation command: `/benchmark-triage $benchmark_path`

Assumptions:

- The confirmed session summary in `/home/adam/.agents/skills/skillify/evals/files/forked-benchmark-triage.md` is treated as the completed interview and source of truth.
- `$benchmark_path` may point either to a `benchmark.json` file or to an iteration directory that contains benchmark results plus nearby eval artifacts.
- The workflow should run as a forked, self-contained skill and use Task-agent deep dives for independent per-eval inspections.
- Allowed tools were captured narrowly from the confirmed session: `Read`, `Grep`, `Glob`, `Edit`, `Write`, and `Bash(python:*)`.
