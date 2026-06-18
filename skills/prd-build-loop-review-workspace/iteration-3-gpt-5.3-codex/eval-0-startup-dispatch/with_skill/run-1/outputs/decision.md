Source of truth: `evals/files/startup-fixture/prd.json` (`prd_file`) is official; `evals/files/startup-fixture/progress.txt` (`progress_file`) is supplemental resume data only.
Resolved `progress_file`: `evals/files/startup-fixture/progress.txt` (dirname(`prd_file`) + `/progress.txt`).
Selected story: `story-auth-timeout` (priority 1), highest-priority `passes: false` story in `prd_file`.
Before any story-specific repo discovery: invoke `subagent-model-router`, then dispatch fresh `implementer`; until dispatch, read only `prd_file`, `progress_file`, and nearby `AGENTS.md` needed to dispatch work.
