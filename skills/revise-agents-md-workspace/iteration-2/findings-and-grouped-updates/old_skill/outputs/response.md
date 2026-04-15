## Findings

Across skill evaluation work, these recurring patterns emerged:

- **Evaluation workspace layout**: Clean `eval-*/` directories are critical; mixed descriptive formats cause parsing/sorting errors in eval-viewer
- **Subagent tool configuration**: Explore mode restricts file/terminal tools; default `runSubagent` permits output writes—choose appropriately by eval requirements
- **Assertion design**: Discriminating assertions (phase completeness checks, explicit test validation) yield measurable pass-rate improvements (+0.07 delta); generic assertions do not
- **Failure templates**: Explicit guardrail rules (e.g., avoid "planning-ready" on auth failure) improve reliability and reduce token variance
- **Testing tool quirks**: Python 3.14 pytest import hangs—use `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q` first; fall back to `unittest` if needed

## Proposed Updates by File Path

### Update: `/home/adam/.agents/AGENTS.md` (create or update)

**Why:** Central guidance for skill development and evaluation across the workspace

```diff
+ ## Skill Evaluation & Workspace Structure
+ - Eval-viewer layout: keep `eval-*/run-*/` structure clean; mixed directory names cause sort/parse failures
+ - Benchmark normalization: sanitize iteration folders to contain only `eval-*` + benchmark files before `aggregate_benchmark`
+ - Subagent selection: Explore mode lacks file/terminal; use default `runSubagent` when eval needs output writing
+ - Assertion design: discriminating assertions (phase completeness, explicit test checks) beat generic assertions; expect +0.07 improvement delta
+ - Failure templates: explicit guardrails (e.g., block "planning-ready" on gh-access fail) improve pass rate; avoid broad catch-alls
+ 
+ ## Environment Quirks
+ - Python 3.14 pytest hangs on plugin autoload; use `PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 pytest -q` or fall back to `unittest`
```
