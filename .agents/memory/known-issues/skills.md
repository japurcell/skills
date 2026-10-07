---
type: Known Issue
description: Known issues, quirks, and workarounds for `skills`.
---

# Skills - Known Issues

Layer-specific quirks for skills. Cross-cutting issues live in `.agents/memory/KNOWN_ISSUES.md`.

**Affected area:** `skills/*/SKILL.md`
**Description:** `python3 skills/skill-creator/scripts/quick_validate.py` rejects `disable-model-invocation` frontmatter even when a skill needs to keep it.
**Workaround:** Preserve the key when a human has approved it; expect validation to fail until the validator supports it.

**Affected area:** `skills/dotnet-upgrade/`
**Description:** The requested `disable-model-invocation: true` frontmatter intentionally retains the incompatibility above. Its `agents/openai.yaml` also sets `policy.allow_implicit_invocation: false`; equivalent enforcement in Copilot CLI and Gemini CLI is not verified.
**Workaround:** Preserve both controls, do not run or modify the rejecting validator for this document-only acceptance, and do not claim universal enforcement. See [client usage](../../../skills/dotnet-upgrade/references/client-usage.md) for dated evidence and limitations.

**Affected area:** `skills/skill-creator/scripts/quick_validate.py`
**Description:** The validator requires the undeclared `PyYAML` package and fails with `ModuleNotFoundError: No module named 'yaml'` when it is unavailable.
**Workaround:** Do not install dependencies implicitly. Run it with the checked-in runtime: `PYTHONPATH=scripts/vendor python3 skills/skill-creator/scripts/quick_validate.py skills/<skill-name>`.

**Affected area:** Maintained evaluation fixtures under `skills/handoff/evals/files/`
**Description:** Repository-wide log and release-directory ignores can silently exclude synthetic inputs needed for fixture reproduction.
**Workaround:** Keep narrow `.gitignore` exceptions for maintained fixture inputs and verify them with `git ls-files --others --exclude-standard` before staging. Do not treat generated run logs as maintained fixtures.

**Affected area:** `skills/skill-creator/scripts/aggregate_benchmark.py`
**Description:** Missing duration becomes zero, output characters can become the token proxy, metadata defaults to three runs, and the delta follows discovered configuration order.
**Workaround:** Preserve raw results, state which runs were selected, correct metadata and delta direction, and omit unavailable time/token metrics from reported comparisons. A single selected run per scenario does not establish repeated-run variance.
