# Skill Audit Batch Sizing Evidence

Static inventory for sizing later audit batches. It does not certify fixture readiness, dependency closure, skill quality, or evaluation quality.

- Inspected: 2026-10-01
- Source commit: `f982ded70a18891781e2f047ff0d3a290828ea4b` (`HEAD`)
- Scope source: [local inventory](local-inventory.md#current-audit-scope), narrowed by [ownership decision](tickets/decide-skill-ownership-and-import-handling.md#resolution).
- Measurement: regular-file byte sizes under each candidate directory; supporting counts exclude the entry `SKILL.md`, every `evals/` subtree, every `*-workspace/` subtree, and `outputs/` subtrees. Eval column checks only for `evals/evals.json`. Lines are decoded only as byte line splits for non-protected skills.
- Protected exception: for `skills/dotnet-upgrade`, `SKILL.md` line count is deferred and its byte size plus bundle totals use filesystem metadata only. The later bounded dependency scan was explicitly authorized to read only `SKILL.md` and `agents/openai.yaml`; no procedure or other bundle content was opened.
- Dependencies column records the bounded static scan of frontmatter, descriptions, headings, explicit skill/reference names, and bundled paths; unmentioned dependencies and closure remain unverified.

| Root | Name | `SKILL.md` lines | `SKILL.md` bytes | Supporting files | Supporting bytes | `evals/evals.json` | Explicit skill/reference dependencies |
| --- | --- | ---: | ---: | ---: | ---: | :---: | --- |
| `skills` | `adversarial-review` | 19 | 659 | 1 | 199 | yes | `SKILL.md:9` requires `delegate-to-subagents` and dispatches an adversarial reviewer |
| `skills` | `agents-md-improver` | 180 | 5900 | 3 | 9633 | no | `SKILL.md:33,144` -> bundled `references/quality-criteria.md`, `references/templates.md` |
| `skills` | `architecture-design-contest` | 165 | 7405 | 1 | 197 | yes | `SKILL.md:41,142` uses `explore` for code-explorer subagents and requires `delegate-to-subagents` |
| `skills` | `code-modernization` | 127 | 13548 | 19 | 480458 | no | `SKILL.md:6,25,53-71,77-80` -> named CLI prerequisites, bundled image/command docs and subagent roles |
| `skills` | `code-review` | 117 | 5934 | 8 | 8229 | yes | `SKILL.md:20-21,27-28,37,42,48,56-66,80,90` -> bundled references; requires `delegate-to-subagents`, two excluded addy skills, and four subagents |
| `skills` | `code-simplify` | 22 | 1087 | 0 | 0 | no | `SKILL.md:6,10` -> requires excluded `addy-code-simplification` and `delegate-to-subagents` |
| `skills` | `commit` | 104 | 3678 | 4 | 3047 | yes | `SKILL.md:51,62,74-75` -> bundled branch-names, message, PR, and dry-run references |
| `skills` | `create-agentsmd` | 247 | 7887 | 1 | 164 | no | No explicit dependency identified in bounded scan; closure unverified |
| `skills` | `create-skill` | 99 | 7653 | 0 | 0 | yes | `SKILL.md:3,12,45-49` -> excluded `skill-creator`, its bundled scripts, grader and repository installer |
| `skills` | `delegate-to-subagents` | 308 | 12184 | 0 | 0 | no | `SKILL.md:17,85` -> requires `subagent-model-router` |
| `skills` | `dotnet` | 103 | 4971 | 4 | 8023 | yes | `SKILL.md:3,19-22` -> workflow precedence plus four bundled topic references |
| `skills` | `dotnet-ui-app` | 84 | 6145 | 26 | 57577 | no | `SKILL.md:3,22,41-52` -> load `dotnet` first for C#/.NET project or CLI work; bundled section map/framework references |
| `skills` | `dotnet-upgrade` | deferred (protected) | 5746 | 45 | 388530 | yes | `SKILL.md:15-19,23-28`; `agents/openai.yaml:2` -> optional `dotnet`/`official-sources`, bundled refs/templates, implicit invocation disabled |
| `skills` | `execplan-implement` | 80 | 5537 | 2 | 1469 | no | `SKILL.md:11,19,32,34` -> required `exec-plans`, `delegate-to-subagents`, `tdd`; bundled message reference |
| `skills` | `explain-your-thinking` | 14 | 588 | 1 | 43 | no | No explicit dependency identified in bounded scan; closure unverified |
| `skills` | `explore` | 38 | 1305 | 0 | 0 | yes | `SKILL.md:15` -> conditionally loads `delegate-to-subagents` and dispatches `code-explorer` |
| `skills` | `fixing-accessibility` | 136 | 4718 | 0 | 0 | no | No explicit dependency identified in bounded scan; closure unverified |
| `skills` | `gh-cli` | 2187 | 40494 | 0 | 0 | no | `SKILL.md:3,12-14,33-46` -> requires GitHub CLI installation and authentication |
| `skills` | `guidance-review` | 23 | 1229 | 1 | 43 | no | No explicit dependency identified in bounded scan; closure unverified |
| `skills` | `handoff` | 97 | 7387 | 0 | 0 | yes | No explicit dependency identified in bounded scan; closure unverified |
| `skills` | `harness-analysis` | 235 | 12973 | 1 | 182 | yes | No explicit dependency identified in bounded scan; closure unverified |
| `skills` | `improve-repo-harness` | 9 | 404 | 1 | 202 | no | No explicit dependency identified in bounded scan; closure unverified |
| `skills` | `improve-skill` | 86 | 3384 | 0 | 0 | yes | No explicit dependency identified in bounded scan; closure unverified |
| `skills` | `official-sources` | 55 | 3121 | 0 | 0 | yes | `SKILL.md:48` -> loads `delegate-to-subagents` when useful |
| `skills` | `prd` | 163 | 8098 | 1 | 147 | no | `SKILL.md:16,29-30` -> conditionally loads `explore`, directly loads `delegate-to-subagents` |
| `skills` | `prd-ralph` | 187 | 6856 | 5 | 8056 | no | `SKILL.md:15,23,38-42,89,107-109,135` -> optional `commit` input flag, required `tdd`, and five bundled workflow references; flag is not a `commit` skill dependency |
| `skills` | `prd-ralph-loop` | 40 | 1780 | 0 | 0 | yes | `SKILL.md:19,21,29` -> loads `delegate-to-subagents`, dispatches `prd-ralph`, then loads `self-improve` |
| `skills` | `self-improve` | 50 | 2432 | 2 | 4614 | yes | No explicit dependency identified in bounded scan; closure unverified |
| `skills` | `spec-to-tasks` | 100 | 3716 | 3 | 3594 | yes | `SKILL.md:35,38,40,47-48,76` -> `delegate-to-subagents`, conditional `explore`, three bundled references and a named validation script |
| `skills` | `subagent-model-router` | 168 | 8127 | 5 | 23097 | no | `SKILL.md:73,75-78,164-168` -> five bundled routing references |
| `skills` | `techdebt` | 98 | 3048 | 1 | 210 | yes | `SKILL.md:13,30,74` -> `delegate-to-subagents`, `explore`, conditional `tdd` |
| `skills` | `to-issues` | 84 | 3319 | 0 | 0 | no | `SKILL.md:11,17,53-55` -> named setup command and issue-tracker access |
| `.agents/skills` | `clean-agent-docs` | 52 | 2066 | 2 | 3642 | no | `SKILL.md:19,26-27` -> two bundled references; requires `update-agent-docs` |
| `.agents/skills` | `exec-plans` | 171 | 16968 | 0 | 0 | no | No explicit dependency identified in bounded scan; closure unverified |
| `.agents/skills` | `ingest-source` | 38 | 1321 | 0 | 0 | no | `SKILL.md:24` -> requires `update-agent-docs` |
| `.agents/skills` | `okf-authoring` | 22 | 2529 | 2 | 2747 | yes | `SKILL.md:14,16,20` -> bundled profile/source-summary references, `update-agent-docs`, and `scripts/lint-okf.py` |
| `.agents/skills` | `update-agent-docs` | 48 | 2248 | 3 | 4919 | no | `SKILL.md:22` -> invokes `okf-authoring` after semantic changes |

## Scope and exclusions

Included: the 32 published candidates and five repository-local candidates listed in the inventory. Exact configured-import exclusions are `caveman`, `frontend-design`, `skill-creator`, `code-review-biaxis`, `codebase-design`, `improve-codebase-architecture`, `prototype`, `research`, `resolving-merge-conflicts`, `tdd`, `wayfinder`, `retro`, `grilling`, `teach`, `writing-for-agents`, `web-accessibility`, `web-best-practices`, `web-performance`, `show-me`, `addy-code-review-and-quality`, `addy-code-simplification`, `addy-performance-optimization`, and `addy-security-and-hardening`.

No historical provenance recovery was performed. Additional exclusions, if encountered, require clear import evidence; an absent importer mapping does not establish repository authorship. Shared resources are considered only when explicitly referenced by an included candidate.

## Explicit dependency observations (bounded scan)

- `skills/architecture-design-contest/SKILL.md:142` directly requires `delegate-to-subagents`, a strong cross-skill grouping anchor.
- `skills/adversarial-review/SKILL.md:9` also requires `delegate-to-subagents`; `skills/architecture-design-contest/SKILL.md:41` additionally loads `explore` for its code-explorer subagents.
- `skills/delegate-to-subagents/SKILL.md:17,85` requires `subagent-model-router`, another direct grouping edge.
- `skills/code-review/SKILL.md:27-28,56-58` requires `delegate-to-subagents` and two excluded addy skills (`addy-code-review-and-quality`, `addy-security-and-hardening`); `:58` names an `addy-test-engineer` role but no corresponding skill. Line `:66` requires four catalog subagents. Its bundled reference set is named at `:20-21,37,42,48,60-64,80,90`.
- `skills/code-modernization/SKILL.md:6,25,53-71` names external analysis tools and bundled image/command documents; `:77-80` lists subagent roles. Exact execution dependencies remain out of scope.
- `skills/agents-md-improver/SKILL.md:33,144` points to two bundled reference files; `skills/commit/SKILL.md:51,62,74-75` points to four bundled workflow references.
- `skills/create-skill/SKILL.md:3,12,45-49` directs broader authoring to the excluded `skill-creator` and names its scripts plus the repository installer. `skills/execplan-implement/SKILL.md:19,32` explicitly activates `exec-plans`, `delegate-to-subagents`, and excluded `tdd`; `skills/explore/SKILL.md:15` also loads `delegate-to-subagents`.
- `skills/official-sources/SKILL.md:48` also loads `delegate-to-subagents` when useful. `skills/gh-cli/SKILL.md:12-14,33-46` names external `gh` installation and authentication prerequisites.
- Planning links: `skills/prd/SKILL.md:16,29-30` uses `explore` and `delegate-to-subagents`; `skills/spec-to-tasks/SKILL.md:35,38,40` uses `delegate-to-subagents` and `explore`; `skills/prd-ralph-loop/SKILL.md:19,21,29` chains `delegate-to-subagents`, `prd-ralph`, and `self-improve`.
- `skills/techdebt/SKILL.md:13,30,74` uses `delegate-to-subagents` and `explore`, with conditional `tdd`. `skills/prd-ralph/SKILL.md:89` also requires `tdd` and names bundled references at `:23,38-42,103,107-109,135`; `skills/subagent-model-router/SKILL.md:73,75-78,164-168` points to five bundled routing references.
- `skills/to-issues/SKILL.md:11,17,53-55` expects a named setup command when tracker context is missing and uses issue-tracker access; implementation of that command is outside this bounded scan.
- Repository-local documentation chain: `.agents/skills/clean-agent-docs/SKILL.md:19,26-27` points to two bundled references and requires `update-agent-docs`; `.agents/skills/ingest-source/SKILL.md:24` also requires it. `.agents/skills/update-agent-docs/SKILL.md:22` invokes `okf-authoring`, whose `:14,20` names two bundled references and `scripts/lint-okf.py`. This is a direct grouping cluster.
- .NET grouping anchors: `skills/dotnet/SKILL.md:3` gives `dotnet` precedence over `prd-*` and `code-review`; `skills/dotnet-upgrade/SKILL.md:19` treats `dotnet` and `official-sources` as compatible skills when available, says absence does not block, and says not to auto-invoke `code-modernization`. The same entry point names bundled references/templates at `:15-17,23-28`; `skills/dotnet-upgrade/agents/openai.yaml:2` disables implicit invocation.
- `skills/dotnet-ui-app/SKILL.md:3` requires loading `dotnet` first for C#/.NET project or CLI work. `skills/code-simplify/SKILL.md:6,10` requires excluded `addy-code-simplification` plus `delegate-to-subagents`; `skills/prd-ralph/SKILL.md:15,89` defines an optional `commit` input flag and requires `tdd`. The input flag does not establish a dependency on the `commit` skill.
- No dependency closure was inferred from unmentioned files. No procedure was activated; the `dotnet-upgrade` paper scan remained limited to its entry-point `SKILL.md` and `agents/openai.yaml`.

## Resource-heavy supporting corpora

The supporting corpus tables below record paths and filesystem sizes. No listed supporting-file contents were read except `skills/dotnet-upgrade/agents/openai.yaml` under the bounded authorization above.

### `skills/code-modernization`

| Path | Bytes |
| --- | ---: |
| `skills/code-modernization/agents/openai.yaml` | 202 |
| `skills/code-modernization/assets/topology-viewer-screenshot.jpg` | 228387 |
| `skills/code-modernization/assets/topology-viewer.html` | 80974 |
| `skills/code-modernization/commands/modernize-assess.md` | 11395 |
| `skills/code-modernization/commands/modernize-brief.md` | 9050 |
| `skills/code-modernization/commands/modernize-extract-rules.md` | 5875 |
| `skills/code-modernization/commands/modernize-harden.md` | 7472 |
| `skills/code-modernization/commands/modernize-map.md` | 8937 |
| `skills/code-modernization/commands/modernize-preflight.md` | 12582 |
| `skills/code-modernization/commands/modernize-reimagine.md` | 6765 |
| `skills/code-modernization/commands/modernize-status.md` | 3030 |
| `skills/code-modernization/commands/modernize-transform.md` | 5888 |
| `skills/code-modernization/commands/modernize-uplift.md` | 24525 |
| `skills/code-modernization/workflows/extract-rules.js` | 16777 |
| `skills/code-modernization/workflows/harden-scan.js` | 10683 |
| `skills/code-modernization/workflows/portfolio-assess.js` | 5877 |
| `skills/code-modernization/workflows/reimagine-scaffold.js` | 5272 |
| `skills/code-modernization/workflows/uplift-deltas.js` | 14233 |
| `skills/code-modernization/workflows/uplift-migrate.js` | 22534 |

### `skills/dotnet-upgrade`

| Path | Bytes |
| --- | ---: |
| `skills/dotnet-upgrade/agents/openai.yaml` | 43 |
| `skills/dotnet-upgrade/assets/templates/candidate-lessons.md` | 3038 |
| `skills/dotnet-upgrade/assets/templates/compatibility-matrix.md` | 3090 |
| `skills/dotnet-upgrade/assets/templates/execplan.md` | 9536 |
| `skills/dotnet-upgrade/assets/templates/inventory.md` | 5579 |
| `skills/dotnet-upgrade/assets/templates/stage-evidence.md` | 6940 |
| `skills/dotnet-upgrade/references/case-studies/workplan-reports.md` | 18816 |
| `skills/dotnet-upgrade/references/client-usage.md` | 8632 |
| `skills/dotnet-upgrade/references/document-review.md` | 8011 |
| `skills/dotnet-upgrade/references/lessons.md` | 9114 |
| `skills/dotnet-upgrade/references/official-sources.md` | 6365 |
| `skills/dotnet-upgrade/references/playbook.md` | 8064 |
| `skills/dotnet-upgrade/references/provenance/original-prompt.md` | 1957 |
| `skills/dotnet-upgrade/references/provenance/source-map.json` | 199525 |
| `skills/dotnet-upgrade/references/routes/net8-to-net10/dependency-compatibility/compatibility-matrix.md` | 13844 |
| `skills/dotnet-upgrade/references/routes/net8-to-net10/dependency-compatibility/official-package-evidence.md` | 10247 |
| `skills/dotnet-upgrade/references/routes/net8-to-net10/dotnet-10/aspnet-core.md` | 4127 |
| `skills/dotnet-upgrade/references/routes/net8-to-net10/dotnet-10/containers.md` | 1785 |
| `skills/dotnet-upgrade/references/routes/net8-to-net10/dotnet-10/core-libraries.md` | 5060 |
| `skills/dotnet-upgrade/references/routes/net8-to-net10/dotnet-10/cryptography.md` | 2533 |
| `skills/dotnet-upgrade/references/routes/net8-to-net10/dotnet-10/entity-framework-core.md` | 5892 |
| `skills/dotnet-upgrade/references/routes/net8-to-net10/dotnet-10/extensions.md` | 1940 |
| `skills/dotnet-upgrade/references/routes/net8-to-net10/dotnet-10/globalization.md` | 680 |
| `skills/dotnet-upgrade/references/routes/net8-to-net10/dotnet-10/index.md` | 2123 |
| `skills/dotnet-upgrade/references/routes/net8-to-net10/dotnet-10/install-tool.md` | 738 |
| `skills/dotnet-upgrade/references/routes/net8-to-net10/dotnet-10/interop.md` | 1016 |
| `skills/dotnet-upgrade/references/routes/net8-to-net10/dotnet-10/networking.md` | 1802 |
| `skills/dotnet-upgrade/references/routes/net8-to-net10/dotnet-10/reflection.md` | 887 |
| `skills/dotnet-upgrade/references/routes/net8-to-net10/dotnet-10/sdk-msbuild.md` | 6489 |
| `skills/dotnet-upgrade/references/routes/net8-to-net10/dotnet-10/serialization.md` | 914 |
| `skills/dotnet-upgrade/references/routes/net8-to-net10/dotnet-10/windows-forms.md` | 1461 |
| `skills/dotnet-upgrade/references/routes/net8-to-net10/dotnet-10/wpf.md` | 666 |
| `skills/dotnet-upgrade/references/routes/net8-to-net10/dotnet-9/aspnetcore.md` | 4251 |
| `skills/dotnet-upgrade/references/routes/net8-to-net10/dotnet-9/containers-deployment.md` | 2084 |
| `skills/dotnet-upgrade/references/routes/net8-to-net10/dotnet-9/core-libraries.md` | 5521 |
| `skills/dotnet-upgrade/references/routes/net8-to-net10/dotnet-9/cryptography.md` | 1873 |
| `skills/dotnet-upgrade/references/routes/net8-to-net10/dotnet-9/csharp-13.md` | 1434 |
| `skills/dotnet-upgrade/references/routes/net8-to-net10/dotnet-9/ef-core.md` | 5993 |
| `skills/dotnet-upgrade/references/routes/net8-to-net10/dotnet-9/index.md` | 1966 |
| `skills/dotnet-upgrade/references/routes/net8-to-net10/dotnet-9/interop-jit.md` | 1203 |
| `skills/dotnet-upgrade/references/routes/net8-to-net10/dotnet-9/networking.md` | 2184 |
| `skills/dotnet-upgrade/references/routes/net8-to-net10/dotnet-9/sdk-msbuild.md` | 2563 |
| `skills/dotnet-upgrade/references/routes/net8-to-net10/dotnet-9/serialization.md` | 1404 |
| `skills/dotnet-upgrade/references/routes/net8-to-net10/dotnet-9/windows-forms-wpf.md` | 2331 |
| `skills/dotnet-upgrade/references/routes/net8-to-net10/index.md` | 4809 |

The largest supporting entry is `references/provenance/source-map.json` at 199,525 bytes; it is listed from metadata only and was not opened. The dependency scan opened only `SKILL.md` and `agents/openai.yaml` after the human's narrow exception; every other upgrade resource remains unread.

### Ten largest `skills/dotnet-ui-app` supporting files

| Path | Bytes |
| --- | ---: |
| `skills/dotnet-ui-app/references/winui/build-run-and-launch-verification.md` | 5012 |
| `skills/dotnet-ui-app/references/winui/foundation-setup-and-project-selection.md` | 4517 |
| `skills/dotnet-ui-app/references/winui/foundation-environment-audit-and-remediation.md` | 3713 |
| `skills/dotnet-ui-app/references/common/testing-debugging-and-review-checklists.md` | 3480 |
| `skills/dotnet-ui-app/references/winui/foundation-template-first-recovery.md` | 3359 |
| `skills/dotnet-ui-app/references/winui/shell-navigation-and-windowing.md` | 3340 |
| `skills/dotnet-ui-app/references/winui/windows-app-sdk-lifecycle-notifications-and-deployment.md` | 2890 |
| `skills/dotnet-ui-app/references/avalonia/build-run-and-launch-verification.md` | 2799 |
| `skills/dotnet-ui-app/configs/winui-config.yaml` | 2564 |
| `skills/dotnet-ui-app/references/winui/foundation-winui-app-structure.md` | 2486 |

## Delegation and Verification

The first sizing explorer used explicitly selected and submitted `gpt-6-luna` at `max` effort. Its 300-second target was interrupted at the parent's 332-second check, 32 seconds late. It saved the measurable table and resource listings, but not the dependency report. A single 60-second report-only recovery on the same configured agent was cancelled when the human questioned repeated interruptions. These stops were parent-imposed limits, not demonstrated crashes or reasoning failures.

The human then approved a longer fact-gathering limit with checkpoint status checks. The canonical rule lives in [repository workflow guidance](../../.agents/instructions/repo.md#subagent-checkpoints). A narrower dependency explorer used explicitly selected and submitted `gpt-6-luna` at `max`, with a 1,200-second initial limit and 300-second checkpoint interval. The parent observed completion by 2026-10-02 00:26:13 UTC, 678 seconds after its recorded dispatch clock. It completed without interruption or a limit extension. Executed model/effort values are unconfirmed; no usage figures were reported. Catalog routing was provisional Standard, with an unused `gpt-5.6-luna`/`max` fallback; desktop prices were unavailable.

The parent independently verified all 37 line/byte/support/eval-presence measurements, retaining the protected line-count exception. Source checks corrected a missed required router dependency, the distinction between two imported Addy skills and three Addy subagent roles, the `commit` input flag versus a skill dependency, and the conditional .NET scope. A literal-name pass broadened dependency coverage, but names alone do not prove dependency type or closure. No grader, scenario, installer, model baseline, migration, or bundle workflow was executed.

## Reproduction approach

Use `rtk git rev-parse HEAD` to capture the source commit. Use `rtk proxy python3` with a read-only `os.walk` over the listed candidate directories and `lstat().st_size` for regular-file totals; omit `evals/`, `*-workspace/`, and `outputs/` subtrees and the entry `SKILL.md` from supporting totals. For non-protected skills, line count is `len(SKILL.md bytes.splitlines())`. To reproduce the original protected measurement, do not read `dotnet-upgrade` file contents: derive bytes and bundle totals from filesystem metadata and leave line count deferred. Determine eval presence by testing only `evals/evals.json`. The later paper-reading exception and bounded dependency scan are separate evidence phases.
