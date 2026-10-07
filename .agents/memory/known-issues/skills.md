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

**Affected area:** Delegation/discovery, quality/harness, requirements/planning and execution/handoff benchmark grading.
**Description:** Artifact predicates do not establish performed workflow, and helper success can omit grading eligible runs. Code Review and Spec to Tasks oracles disagree with their maintained contracts; Harness Analysis's lexical checks miss claim polarity and section meaning. Loop paper cases do not establish blind orchestration; Handoff grading rejects a valid named path; Loop/Commit grading inspects unrelated current-source headings. The [findings register](../../../docs/skill-audit/findings.md) owns DD-001/DD-003/DD-004, QH-001/QH-007, RPT-001 and EH-001/EH-003/EH-009 evidence and proposal status; no native failure or source repair is established. Accepted scope includes exactly Loop/Commit/Handoff additions, retaining earlier targets for twelve metric producers and nine protocol graders. Unknown representation and failure outcomes remain pending; scope acceptance does not authorize execution.
**Workaround:** Keep independently useful artifact checks separate from trace-backed workflow evidence, verify eligible-run accounting, and leave unknown measurements unresolved. Exact failure outcomes and unknown-metric representation remain human decisions; this pointer does not choose protocols or authorize grader edits.

**Affected area:** Quality/harness and architecture-contest caller/helper contracts.
**Description:** Code Review requires a `generalist` without a repository source definition and a Fast filter tier that can conflict with required review floors. Techdebt's rollback wording and Explore/TDD consumer branches have competing readings. Architecture Contest's explorer minimum conflicts with Explore's narrow no-agent branch. [QH-002 through QH-006](../../../docs/skill-audit/findings.md#qh-002-required-generalist-role-lacks-a-repository-source-definition) and [RPT-003](../../../docs/skill-audit/findings.md#rpt-003-architecture-contest-conflicts-with-explores-narrow-branch) own evidence and pending routes; source absence does not prove universal host unavailability.
**Workaround:** Retain required roles, helpers, approvals and stops. Resolve the exact contract before rewriting dependent instructions; do not silently replace roles, waive dependencies or infer rollback authority from ambiguous text.

**Affected area:** Planning workflows and downstream verification prerequisites.
**Description:** To Issues names an unshipped setup helper for missing tracker/labels; PRD and Spec to Tasks prescribe a `playwright-cli` browser helper whose supply is not documented here. [RPT-002](../../../docs/skill-audit/findings.md#rpt-002-to-issues-names-an-unshipped-setup-helper) and [RPT-005](../../../docs/skill-audit/findings.md#rpt-005-ui-planning-prescribes-an-unshipped-browser-helper) own the exact source and proposed decisions. Browser wording is a downstream acceptance requirement, not a browser invocation during planning; repository absence does not establish universal host unavailability.
**Workaround:** Verify supported helper supply and retain tracker/label knowledge, live publication approval and UI verification. Do not invent setup authority, substitute helper identities or mark downstream verification performed from planning text. Exact dependency mappings remain pending human decisions.

**Affected area:** Ralph/Loop failure recovery and required TDD approval ordering.
**Description:** Loop's three-failure stop and delegation's one-replacement exception lack a shared category/consent definition for repeated failures; terminal maintenance after a failure stop is unspecified. Ralph's no-interview instruction leaves missing TDD seam approval and refactor-stage precedence unresolved. [EH-005](../../../docs/skill-audit/findings.md#eh-005-ralph-loop-failure-counting-and-retry-consent-are-unresolved) and [EH-006](../../../docs/skill-audit/findings.md#eh-006-ralph-and-tdd-have-unresolved-approval-and-refactor-ordering) own the evidence and proposed routes. Successful distinct task runs are compatible; no failed native run or extra retry authorization is established.
**Workaround:** Preserve blind task selection, both retry limits, required TDD and approval before tests. Resolve the exact consumer branch before dependent wording or execution; do not relabel retries as new tasks, infer consent or make the imported helper optional.

**Affected area:** Execplan integration validation and published ExecPlans helper supply.
**Description:** Conflict-free rebase can change the integrated behavior, while the caller's no-rerun instruction and tested-tip requirement lack a reconciled validation state. The required ExecPlans helper exists in repository-local source but is outside published installer selection. [EH-007](../../../docs/skill-audit/findings.md#eh-007-execplan-integration-has-unresolved-tested-tip-validation) and [EH-008](../../../docs/skill-audit/findings.md#eh-008-published-execplan-requires-a-helper-with-unestablished-supply) own exact evidence and proposed routes. No integration regression is observed; repository absence does not prove universal host unavailability.
**Workaround:** Retain mandatory ExecPlans, isolated workers, serial clean integration and repair stops. Establish supported helper supply and the tested-state contract before dependent changes; do not infer validation from conflict absence or publish the protected local helper by assumption.

**Affected area:** Commit dry-run inspection, mutation and output authority.
**Description:** The numbered one-commit step precedes dry-run handling, and the dry-run report reference supplies no earlier mutation gate. Paper cases prohibit git and cannot establish native dry-run behavior. [EH-010](../../../docs/skill-audit/findings.md#eh-010-commit-dry-run-mutation-and-output-boundaries-are-unclear) owns the static evidence and proposed authority decision; no unintended commit was observed.
**Workaround:** Resolve allowed read-only inspection, excluded mutations and no-SHA output before dependent instructions. Preserve real-commit exactly-one behavior, explicit user overrides, staged/generated-artifact scope and publication approval; this issue does not grant mutation authority.
