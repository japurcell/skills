## Findings

The workspace shows consistent patterns across skill development, especially in evaluation methodology and testing. The strongest recurring rules are:

1. **Eval workspace structure**: Iteration folders (iteration-1, iteration-2, etc.) under `SKILL-NAME-workspace/`
2. **Evaluation layout**: `eval-*/` folders containing `<config>/run-*/` subdirectories with `grading.json` results
3. **eval-viewer sensitivity**: Mixed descriptive run directory names cause NoneType sort errors; use sanitized iteration-view folders
4. **Discriminating assertions**: Adding structural assertions (phase completeness + explicit tests) in eval specs improves pass rates measurably
5. **Subagent execution**: Default runSubagent is more capable for executable evals; Explore mode lacks file/terminal tools
6. **Benchmark orientation**: Manually order benchmark.md files lexicographically with `with_skill` first to show meaningful deltas
7. **Python test stability**: Use `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q` for pytest; fallback to unittest for environment issues
8. **Guardrail rules**: Explicit failure-template rules improve consistency and reduce variance more than generic assertions

## Proposed Updates

### Update: `./AGENTS.md`

**Why this file**: Establish shared conventions for skill evaluation, workspace structure, and testing practices that will help future iterations succeed faster.

```diff
+ ## Skill Evaluation Workspace

+ Eval workspaces follow `SKILL-NAME-workspace/iteration-N/` structure with subdirectories for each iteration.
+ Use `eval-*/` folders containing `<config>/run-*/` with `grading.json` results for benchmarking.
+ For eval-viewer review, create clean iteration-view folders with only `eval-*` and benchmark files; mixed run names cause NoneType errors.

+ ## Eval Spec Best Practices

+ Add discriminating structural assertions (explicit phase completeness checks + test assertions) not generic ones; improves pass rates 0.05-0.10 delta.
+ Include explicit failure-template rules as guardrails rather than relying on generic guidelines; reduces token variance and improves consistency.

+ ## Subagent Selection

+ Prefer default `runSubagent` for executable evaluation runs; Explore mode lacks file/terminal tool access needed for real execution.
+ Use Explore mode narrowly for codebase analysis and search; do not use for runs requiring code execution.

+ ## Benchmark Presentation

+ Order benchmark.md files manually by configuration with `with_skill` first to surface meaningful pass-rate deltas clearly.
+ Use aggregate_benchmark with clean eval-* layout; normalize run directory names before aggregation to avoid sort issues.

+ ## Python Environment Testing

+ For pytest: start with `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q` for stability; fallback to unittest if environment issues occur.
+ Document Python version and plugin-loading issues in eval notes if encountered; patterns may differ across environments.
```

---

**Approval request**: Apply these grouped rules to create `./AGENTS.md` for the skills workspace with the proposed diffs above?
