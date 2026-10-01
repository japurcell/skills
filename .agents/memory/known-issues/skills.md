---
type: Known Issue
description: Known issues, quirks, and workarounds for `skills`.
---

# Skills - Known Issues

Layer-specific quirks for skills. Cross-cutting issues live in `.agents/memory/KNOWN_ISSUES.md`.

**Affected area:** Imported skill directories and shared references.
**Description:** [Addy refresh](../../../scripts/addy-install.sh) deletes and recopies selected skill directories and its shared reference destination. The [multi-source copy helper](../../../scripts/copy-from-git.sh) overlays matching paths without destination cleanup, so local edits can be overwritten while stale files remain. `.addy-skills` records unprefixed source names, not upstream revisions or preserved local changes.
**Workaround:** Do not assume refresh preserves local authoring changes or that its state file proves provenance. Inspect the relevant source and current changes before a human-run refresh; import orchestration remains human-only under [scripts instructions](../../instructions/scripts.md).

**Affected area:** `skills/*/SKILL.md`
**Description:** `python3 skills/skill-creator/scripts/quick_validate.py` rejects `disable-model-invocation` frontmatter even when a skill needs to keep it.
**Workaround:** Preserve the key when a human has approved it; expect validation to fail until the validator supports it.

**Affected area:** `skills/dotnet-upgrade/`
**Description:** The requested `disable-model-invocation: true` frontmatter intentionally retains the incompatibility above. Its `agents/openai.yaml` also sets `policy.allow_implicit_invocation: false`; equivalent enforcement in Copilot CLI and Gemini CLI is not verified.
**Workaround:** Preserve both controls, do not run or modify the rejecting validator for this document-only acceptance, and do not claim universal enforcement. See [client usage](../../../skills/dotnet-upgrade/references/client-usage.md) for dated evidence and limitations.

**Affected area:** `skills/skill-creator/scripts/quick_validate.py`
**Description:** The validator requires the undeclared `PyYAML` package and fails with `ModuleNotFoundError: No module named 'yaml'` when it is unavailable.
**Workaround:** Do not install dependencies implicitly. Run it with the checked-in runtime: `PYTHONPATH=scripts/vendor python3 skills/skill-creator/scripts/quick_validate.py skills/<skill-name>`.
