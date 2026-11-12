# Accomplishment report maintenance

This opt-in Forest Service skill produces one concise, copy-ready accomplishment paragraph and brief calculation notes for a completed ExecPlan. It activates `exec-plans` for plan interpretation and `agency-priorities` for supported alignment. Its description enables model invocation at closeout; it does not install a filesystem hook or change the shared planning skill.

## Invocation

Optionally pass the hourly wage and currency as a skill argument: `$accomplishment-report --hourly-wage 100 USD` (or `/accomplishment-report --hourly-wage 100 USD` on slash-command hosts). This supplies USD 100 per human hour for the current report. An explicit argument overrides older rates. When omitted, use a user-supplied task rate or ask for the wage and currency, including at automatic closeout. Keep the report pending and finish it after the answer without requiring another invocation. Invalid or incomplete arguments require correction before a cost claim.

## Evaluation

`evals/evals.json` contains creation, revision, and incomplete-work scenarios with realistic wage and effort evidence, plus missing-wage, insufficient-effort, zero-savings, negative-savings, explicit-argument, and invalid-argument branches. Each `files` entry points to a reusable input under `evals/fixtures/`; scenarios may share a fixture. For every run, copy the referenced fixture contents into a fresh isolated run root, run the prompt there with the exact local skill or without it, and keep generated outputs in a sibling `accomplishment-report-workspace/iteration-N/`, outside this installed bundle. Never run a scenario against the shared fixture itself.

For a scenario with `follow_up_prompt`, first capture the initial response, then send that field as a separate user turn in the same session. Keep it hidden until that turn; do not include it in the initial prompt. Retain both turns and the resulting files so clarification and completion can be checked separately.

For each scenario, inspect the paragraph, calculation notes, and action transcript against every assertion. Verify the destination and preservation of existing content. Recalculate savings independently, check that missing wage leads to a question followed by a saved report once answered, and confirm that incomplete work produces no report. Treat unavailable output as failed, not a passing absence check.

Before running, confirm each rate and hour estimate required by the rubric is present in the prompt or fixture. Keep missing inputs intentional in clarification scenarios.

Executing agents receive only the prompt and fixture files. Keep `expected_output` and assertions out of their context; provide them only to graders after the run is complete.

Fixtures are synthetic; their assumptions are not real project measurements. AI tool spend and net-cost claims are outside this skill's labor-savings measure.

Check bundle metadata with the available skill-creator `scripts/quick_validate.py`, and from the repository root run `python3 scripts/validate-skill-sources.py skills`. Review report quality as well as assertion totals. One sample per scenario does not establish reliability, trigger performance, or productivity gains.

## Authoring basis

The model-invoked description and minimal frontmatter follow the [skill frontmatter reference](https://code.claude.com/docs/en/skills#frontmatter-reference). Runtime instructions stay concise and evaluation guidance remains separate, following the [effective-skills guidance](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#checklist-for-effective-skills), consulted 2026-10-21.
