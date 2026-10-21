# Accomplishment report maintenance

This opt-in Forest Service skill produces a sibling Markdown report for a completed ExecPlan. It activates `exec-plans` for plan interpretation and `agency-priorities` for strategic alignment. Its description enables model invocation at closeout; it does not install a filesystem hook or change the shared planning skill.

## Evaluation

`evals/evals.json` contains three synthetic scenarios: completed work with known base costs, an existing report with unsupported savings and missing telemetry, and stale completion checkboxes with unresolved acceptance. Run each prompt with the exact local skill and without it, using the same model and supplied facts. Keep generated outputs in a sibling `accomplishment-report-workspace/iteration-N/`, outside this installed bundle.

For each scenario, inspect the report and action transcript against every assertion. Verify the destination and preservation of existing content. Calculate all cost rows independently, including negative savings. Confirm that incomplete work produces no report. Treat unavailable output as failed, not a passing absence check: the negative case needs an explicit response explaining the unresolved acceptance.

For the measured fixture, the base case is 24 human-only hours at USD 100/hour, versus 6 assisted human hours plus USD 40 AI spend: USD 2,400 versus USD 640, USD 1,760 estimated savings, 73.33%, and 18 human hours saved. Ten aggregate agent-hours and four elapsed hours are separate measures. Scenario assumptions and simulated evidence are not real project measurements.

Check bundle metadata with the available skill-creator `scripts/quick_validate.py`, and from the repository root run `python3 scripts/validate-skill-sources.py skills`. Review report quality as well as assertion totals. One sample per scenario does not establish reliability, trigger performance, or productivity gains.

## Authoring basis

The model-invoked description and minimal frontmatter follow the [skill frontmatter reference](https://code.claude.com/docs/en/skills#frontmatter-reference). Runtime instructions stay concise and evaluation guidance remains separate, following the [effective-skills guidance](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices#checklist-for-effective-skills), consulted 2026-10-21.
