1. Source of truth: `prd_file` is official story status/completion source; `progress_file` is supplemental resume data only.
2. Resolved `progress_file`: `/home/adam/dev/personal/skills/skills/prd-build-loop-review/evals/files/startup-fixture/progress.txt`.
3. Selected story: `story-auth-timeout` (highest-priority story with `passes: false`, `priority: 1`).
4. Before story-specific discovery: invoke `subagent-model-router`, then dispatch fresh `implementer`; before that first implementer dispatch, read only `prd_file`, `progress_file`, and nearby `AGENTS.md` needed to dispatch work.
