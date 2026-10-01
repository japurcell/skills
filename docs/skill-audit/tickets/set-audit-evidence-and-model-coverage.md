# Set Audit Evidence and Model Coverage

**Type:** grilling
**Status:** closed
**Blocked By:** extract-complete-authoring-checklist.md, establish-provider-compatibility-constraints.md
**Research Dir:** not applicable

## Question

What exact evidence makes this audit complete, and which OpenAI models, client surfaces, scenarios, and repetitions must that evidence cover?

The human chose static review of all in-scope skills plus targeted OpenAI baselines, with broader validation in the ExecPlan. Imported skills are excluded by the ownership decision; do not choose them for this effort's baselines. The requested models are 5.6, 6, and 6.1 Sol; 5.6 and 6 Luna; Astra; and Terra. Set exact model IDs and effort values from verified availability, baseline selection criteria, safe fixtures, trigger and negative-case coverage, grading criteria, and reporting for unavailable execution. Separate audit baselines from later candidate comparisons. Reconcile provider constraints and existing eval coverage. Preserve `dotnet-upgrade` document-only acceptance; do not run privileged workflows to fill a gap or report an unrun test as passing.

The decision must specify a reproducible evidence contract, exact supported model choices or an explicit unresolved prerequisite, and what constitutes a blocking audit gap.

---

## Resolution

The human confirmed all nine evidence policies in four rounds on 2026-10-01. This resolution defines audit evidence and later validation obligations. It does not authorize implementing skill improvements or running baselines in this decision session.

### Static coverage and evidence boundaries

Review every remaining in-scope candidate against the complete authoring checklist and the [adoption rubric](set-adoption-rules-and-protected-behavior.md#resolution). The current pool is 32 published and five repository-local skills; the [ownership decision](decide-skill-ownership-and-import-handling.md#resolution) excludes 23 configured imports and any additional imports established by clear evidence. Record applicability, disposition, current compliance, source anchors, and unresolved evidence separately. Check supporting resources only where an included skill depends on them.

Static evidence can establish a missing file, contradictory instruction, or documented client mismatch. It cannot establish observed execution, successful activation, or universal provider enforcement. Existing evals and graders are evidence inputs, not passing results. Keep the `dotnet-upgrade` exception limited to its approved document and paper-scenario review; do not run its validator, packaging, installer, live models, or migration commands.

### Baseline surface and sample

Use native Codex CLI for audit baselines. Capture the discovered skill set, activation evidence, tool trace, and outputs. Explicit-path instruction replay is supplementary evidence of instruction following; it does not prove native discovery or automatic activation. Copilot and Gemini compatibility remains a static comparison, and desktop behavior remains untested.

Start with up to three fixture-ready, in-scope skills selected for distinct concrete risk patterns, such as triggering, reference retrieval, or stopping and approval behavior. Actual selections belong in the bounded audit/baseline tickets after fixture and finding review; the [evidence facts](../evidence-model-baselines.md) identify candidates without selecting them. Expand the baseline set only for a concrete finding and record the reason and added scope.

For each selected skill, cover explicit invocation, intended automatic activation where allowed, an adjacent negative case, and a relevant failure or protected-boundary case where safe. Use realistic task context rather than simple keyword probes. Respect disabled implicit invocation. Record unavailable safe cases as gaps; do not silently drop them or run privileged workflows to fill them. Run the same selected cases across every model in the matrix below. Record untested skills and behaviors, and do not generalize sample results to the full pool.

### Exact model matrix

The human confirmed that Terra means GPT-5.6 Terra and chose explicit `medium` effort for every audit configuration:

| Requested target | Native CLI model ID | Audit effort |
| --- | --- | --- |
| GPT-5.6 Sol | `gpt-5.6-sol` | `medium` |
| GPT-6 Sol | `gpt-6-sol` | `medium` |
| GPT-6.1 Sol | `gpt-6.1-sol` | `medium` |
| GPT-5.6 Luna | `gpt-5.6-luna` | `medium` |
| GPT-6 Luna | `gpt-6-luna` | `medium` |
| GPT-6 Astra | `gpt-6-astra` | `medium` |
| GPT-5.6 Terra | `gpt-5.6-terra` | `medium` |

The installed CLI catalog advertises all seven IDs and `medium` for each. Catalog advertisement and app dispatch metadata do not prove account access or successful native execution. Recheck the client catalog and exact settings before execution. Capture the requested model and effort, and the resolved values only when runtime evidence reports them. Do not silently substitute an unavailable model, effort, client, or API surface. Results apply only to the tested client and effort; broader settings belong in later candidate validation.

### Repetitions and safe setup

Run each selected model/scenario configuration three times in fresh sessions with fresh fixture state. Keep every attempt, including failures and timeouts. Report per-case results and variation; three runs provide a diagnostic baseline, not a statistical reliability claim.

Use disposable fixture workspaces, restricted tools, and controlled skill discovery. Preserve required dependencies, delegation, and approval behavior. Provision the tested skill and necessary dependencies with explicit paths and record what is discoverable, including competing skills. Do not modify installed copies or rely on an unrecorded duplicate of the tested name. Verify the shipped file set when assessing published behavior; repository-local skills retain their repository context.

No global installer, live repository mutation, publishing, or `dotnet-upgrade` run is part of this baseline scope. Existing safe fixtures may be reset and provisioned; missing fixture creation remains later validation work. Before a run, verify that the client can enforce the required isolation and permissions. A prompt that asks the model to stay in a directory is not evidence of enforced containment. Unsupported isolation remains a gap.

### Grading and reproducibility

Define expected behavior before runs. Use deterministic artifact and trace checks where practical, plus an evidence-cited rubric for judgment. Grade activation, required workflow and approval boundaries, and task output separately. A model's own claim of compliance is not proof. Record evaluator disagreements as unresolved evidence. Preserve finding severity separately from run scores; an observed skill failure is useful audit evidence, not a requirement to implement a fix before reporting it.

Keep an unchanged source snapshot. Record source and fixture hashes, prompt, discovered skill set, client version, exact requested model and effort, reported resolved values, permission and sandbox settings, raw JSONL, outputs, grades and evidence, failures, timing, and reported usage. Do not invent unreported usage or executed settings. Link run artifacts from `docs/skill-audit/`; keep generated runs in the existing sibling workspace layout with one canonical eval directory per scenario and repeat-specific run folders.

These are current-skill diagnostic baselines. They do not prove an authoring improvement. The implementation ExecPlan must define later comparisons against the unchanged pre-edit snapshot using matched scenarios, fixtures, clients, models, and efforts, with broader validation justified by accepted findings.

### Required gaps and downstream work

A failed skill run counts as completed diagnostic evidence when a usable trace supports the result. Separate skill behavior from harness, permission, availability, and infrastructure failures. An unavailable required model, unsafe fixture setup, or missing usable trace remains an incomplete required baseline. Missing evidence never becomes a passing result or proof of incompatibility.

Resolve required gaps or obtain an explicit, scoped human waiver before using the completed-audit label. Available static findings can be published while the baseline remains incomplete. A waiver records the affected skill/scenario/model, reason, user decision, and remaining validation obligation; it does not establish successful behavior. The later completion-gates ticket incorporates this rule without silently weakening it.

This resolution unblocks [Choose Audit Batches and Evidence Format](choose-audit-batches-and-evidence-format.md). That ticket defines bounded review batches and coverage/report records. No audit baseline has run yet.
