Summary from the build workflow:

What the manager hands the implementer (lean handoff):
- The implementer-prompt.md with:
  - Task text + clear success criteria (e.g., "validation runs and exits 0; outputs match expected").
  - Known constraints (no commits, no new deps, test environment).
  - Only known file hints: scripts/addy-install.sh and skills/build/evals/grade_benchmark.py.
  - Explicit validation commands to run (see below).

How the implementer should choose verification (to avoid generic frontend fallbacks):
- Infer the surface: this is shell + Python work. Prefer narrow checks for that stack.
- Run explicit commands the manager provided (examples):
  - bash -n scripts/addy-install.sh
  - bash -x scripts/addy-install.sh --dry-run (or run in ephemeral container) and capture exit code
  - python3 -m pip install -r requirements.txt (if needed) then python3 skills/build/evals/grade_benchmark.py --help
  - python3 skills/build/evals/grade_benchmark.py --run <sample-input> && assert exit code 0 and expected output lines
  - git status --porcelain (collect uncommitted files)
- Record exact commands, outputs, and exit codes in verification context sent onward.

Concrete manager-provided validation commands force a weaker model to run shell/Python checks instead of falling back to generic frontend tooling.
