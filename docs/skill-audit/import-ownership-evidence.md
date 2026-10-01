# Import and Packaging Evidence

Inspected 2026-10-01. These are static observations of checked-in source and current destination files, not importer or installer execution evidence. No upstream repository was fetched, no source-history equivalence was established, and no refresh or installation was run.

## Configured imports

The multi-source importer configures 19 destination entry points. All 19 currently exist. These mappings establish configured origins, not proof that current files match a particular upstream revision.

| Configured source | Destination skills | Mapping evidence |
| --- | --- | --- |
| `JuliusBrussee/caveman` | `caveman` | [import-skill-repos.sh:15](../../scripts/import-skill-repos.sh) |
| `anthropics/claude-plugins-official` | `frontend-design`, `skill-creator` | [import-skill-repos.sh:19](../../scripts/import-skill-repos.sh) |
| `mattpocock/skills` | `code-review-biaxis`, `codebase-design`, `improve-codebase-architecture`, `prototype`, `research`, `resolving-merge-conflicts`, `tdd`, `wayfinder`, `retro`, `grilling`, `teach`, `writing-for-agents` | [import-skill-repos.sh:24](../../scripts/import-skill-repos.sh) |
| `addyosmani/web-quality-skills` | `web-accessibility`, `web-best-practices`, `web-performance` | [import-skill-repos.sh:39](../../scripts/import-skill-repos.sh) |
| `humanlayer/skills` | `show-me` | [import-skill-repos.sh:45](../../scripts/import-skill-repos.sh) |

`frontend-design` imports only its `SKILL.md`; `skill-creator` imports a whole directory. The Matt Pocock code-review source maps to the local name `code-review-biaxis`; most other directory mappings use the source basename. The `show-me` origin corrects the original inventory's unsupported `anthropics/show-me` attribution. Source existence on the remote is not verified here. In particular, the current `improve-codebase-architecture` entry point exists; its absence cannot be inferred from the shorter list of skills with evaluations.

The separate Addy importer defaults to `addyosmani/agent-skills`, a sibling `addy-agent-skills` checkout, and the `addy-` destination prefix ([addy-install.sh:5](../../scripts/addy-install.sh)). [.addy-skills](../../.addy-skills) stores four unprefixed source names: `code-review-and-quality`, `code-simplification`, `performance-optimization`, and `security-and-hardening`. All four prefixed destination entry points currently exist. The state writer records selections or discovered names, not source revisions ([addy-install.sh:484](../../scripts/addy-install.sh)).

Together, these scripts configure import relationships for 23 of the 55 published entry points. The remaining published entry points and all five repository-local entry points still require per-skill origin assessment. An entry point's repository-local workflow role does not prove its historical authorship. Do not classify unlisted skills as repository-authored solely because these import scripts omit them.

## Refresh boundaries

- The multi-source importer first invokes the human-only workspace pull helper ([import-skill-repos.sh:6](../../scripts/import-skill-repos.sh)). The copy helper attempts a fast-forward pull on a matching source clone; its recovery can fetch and hard-reset that clone to the remote default branch ([copy-from-git.sh:115](../../scripts/copy-from-git.sh)).
- The copy helper uses `rsync -a` or `cp -R` without a destination-cleanup operation ([copy-from-git.sh:190](../../scripts/copy-from-git.sh)). Matching destination paths can be overwritten, while unrelated or obsolete files can remain. Treat this as overlay behavior, not a reviewed merge or guaranteed clean snapshot.
- Addy deletes and recopies each selected skill directory, then rewrites its name ([addy-install.sh:454](../../scripts/addy-install.sh)). It also deletes and recopies the shared reference destination ([addy-install.sh:472](../../scripts/addy-install.sh)). Local changes in those destinations are not protected by the refresh.
- These importer paths do not maintain per-skill upstream revision records or local-deviation ledgers. Current destination content needs its own baseline before proposed authoring changes or a reviewed refresh.

These are source-level mutation paths, not proof that a specific local edit has already been lost. [Scripts instructions](../../.agents/instructions/scripts.md) keep orchestration imports human-only. Reading their source does not authorize running them.

## Installed resources

The regular Bash installer reads published skills from `skills/`; it does not install the five repository-local workflow skills from `.agents/skills/` ([install.sh:6](../../scripts/install.sh)). It skips workspace/archive entries and copies skill directories into `~/.agents/skills`, then removes each skill's `evals/`, `README.md`, `LICENSE.txt`, and `LICENSE.md` ([install.sh:40](../../scripts/install.sh)). These removals concern the installed copy, not the checked-in source.

Shared references are copied into `~/.agents/references` when the repository's `references/` source directory exists. The installer creates the destination before copying ([install.sh:193](../../scripts/install.sh)); the destination need not already exist. A focused source check finds the same source-existence condition and destination creation in [install.ps1:479](../../scripts/install.ps1). This corrects the older architecture-table wording that made copying depend on target existence.

Consequently, references to excluded per-skill files and references outside a skill directory require review against the actual installation layout. Bundled resources travel only when their paths survive the installer. Shared resources depend on their source tree and supported installation layout. This evidence does not establish every consumer link, custom installation path, provider's resource access, or cross-platform runtime conformance; those remain separate validation concerns.

## Delegation and verification

    subtask_id: import-ownership-facts
    selected: {model: gpt-6-luna, reasoning_effort: medium}
    submitted: {model: gpt-6-luna, reasoning_effort: medium}
    executed: {model: unconfirmed, reasoning_effort: unconfirmed}
    runtime_limit: {value: 300 seconds, mechanism: parent elapsed-time checks and interruption}
    completion_check: 105 seconds after routing, completed before deadline
    status: completed
    output_verified: true
    routing_compliant: true

The parent checked consequential importer and installer source ranges, the four state-file values, and all 19 configured multi-source destination entry points. Verification corrected the explorer's prefixed state-file wording, rejected an unsupported absence inference, and established the shared-reference source-directory condition. No behavioral run occurred.
