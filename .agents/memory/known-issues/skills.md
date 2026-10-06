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

**Affected area:** Create Skill refresh and repository installer authority.
**Description:** Create Skill requires an account-level refresh after edits, and repo workflow requires installed refresh before live checks, while scripts instructions restrict agents to targeted verification/test scripts. The unresolved cross-file authority conflict is recorded once in [SAG-002](../../../docs/skill-audit/findings.md#sag-002-installer-ownership-conflict).
**Workaround:** Follow the task's actual authorization and [pending authority decision](../../../docs/skill-audit/tickets/resolve-installer-authority-for-skill-authoring.md). This issue record does not select an installer policy or authorize installation, and source edits alone do not prove installed refresh.

**Affected area:** Repository-local agent-document metadata selection.
**Description:** The updater's index/log type table conflicts with the root-only OKF profile and linter precedence; [RLW-001](../../../docs/skill-audit/findings.md#rlw-001-maintenance-type-table-disagrees-with-the-root-only-okf-contract) owns the exact evidence and accepted later authoring proposal. The source repair remains unimplemented.
**Workaround:** Follow the existing [OKF profile](../../skills/okf-authoring/references/profile.md): only root memory INDEX/LOG receive their special types; nested concepts use their matching area/default type. This pointer does not authorize changing the protected local skill bundle.

**Affected area:** Explore and Official Sources benchmark grading.
**Description:** Existing artifact predicates do not establish independent exploration areas or performed citation/cache/fetch behavior, and helper success can omit grading eligible runs. The static findings [DD-001](../../../docs/skill-audit/findings.md#dd-001-explore-spawn-grading-omits-independent-area-assertions), [DD-003](../../../docs/skill-audit/findings.md#dd-003-official-source-graders-equate-text-mentions-with-citation-and-cache-evidence) and [DD-004](../../../docs/skill-audit/findings.md#dd-004-graders-can-announce-success-without-grading-runs-and-do-not-validate-json-shape) own evidence and pending proposals; no native failure or source repair is established.
**Workaround:** Keep independently useful artifact checks separate from trace-backed workflow evidence, verify eligible-run accounting, and leave unknown measurements unresolved. Exact failure outcomes and new metric-consumer targets remain human decisions; this pointer does not choose protocols or authorize grader edits.
