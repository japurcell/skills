Recommended save path: `.agents/skills/benchmark-triage/SKILL.md`

Invocation command: `/benchmark-triage $benchmark_path`

Assumptions:

- The confirmed session summary at `/home/adam/.agents/skills/skillify/evals/files/forked-benchmark-triage.md` is treated as the completed interview record for this benchmark run.
- `$benchmark_path` may point either to a `benchmark.json` file or to an iteration directory that contains one.
- The skill should run in `fork` context and stay self-contained unless required benchmark artifacts are missing.
- Per-eval deep dives should use task agents when reviews are independent.
- The benchmark-analysis tool mix is intentionally narrow: `Read`, `Grep`, `Glob`, `Edit`, `Write`, and `Bash(python:*)` when structured analysis is useful.
