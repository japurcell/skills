# Qualitative ExecPlan authoring evaluation

This case supplements the three deterministic scenarios in `evals.json`. Use evidence review for these assertions; `grade_benchmark.py` intentionally supports only the named deterministic scenarios. Do not pass this case to that CLI or infer these assertions from keyword matches.

## Prototype and migration planning

Copy `files/create-plan/project/` into a disposable run directory and supply `files/prototype-migration/brief.md`. Use the same input tree and prompt for both skill snapshots. Keep each run isolated and retain the resulting `ExecPlan.md` and transcript.

Prompt:

    Use the supplied exec-plans skill to create an implementation-ready ExecPlan for brief.md and the supplied project. Save outputs/ExecPlan.md. Do not edit project code.

Review the plan against these assertions using file and section evidence:

1. It names precise existing and proposed files, edit locations, and required function signatures or interface contracts. A novice can identify how the parser, CLI, and summary implementation connect.
2. It specifies independently runnable feasibility experiments for line parsing and streaming aggregation before integrating them. Each experiment has observable success and failure criteria.
3. It identifies what would promote each prototype into the implementation and what would cause it to be discarded or reworked. Planned results are clearly distinguished from measurements already obtained.
4. It validates the list and stream paths against the same valid, empty, and malformed input, then gates the default switch and legacy-path retirement on evidence. It includes a safe retry or rollback path.
5. It gives exact commands, working directories, expected successful output, invalid-input diagnostics and exit behavior, and how to interpret test failures. At least one demonstration exercises the CLI beyond compilation.
6. It leaves implementation and acceptance open, preserves the default output contract, and makes ordinary planning decisions without asking for routine next steps.

Record each pass/fail with quoted or paraphrased evidence from the produced plan. A passing authored plan is not evidence that the proposed parser, migration, or memory bound works. Single paired runs do not establish general agent-performance differences.
