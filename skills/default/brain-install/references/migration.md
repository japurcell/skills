# Migrate Existing Guidance

## Inventory before editing

Read root and nested AGENTS.md files, provider guidance entrypoints, memory/KB directories, linked references, matching skills, and hooks/configuration that load old guidance. Follow references until each live obligation is accounted for. Include existing brain notes and indexes. Keep target secrets and private history out of generated notes and audits.

Record a concise mapping in `brain/audits/brain-install-migration.md`, linking it from `brain/audits/index.md`. Before the initial index checkpoint, keep the working mapping in temporary session notes so an unacknowledged installer run remains read-only.

Use one row per obligation, including its trigger/condition, scope, exclusions, and approval requirements:

| Source and obligation | Disposition | Exact destination or reason | Verification |
| --- | --- | --- | --- |
| `services/AGENTS.md`: deployment requires approval | retained | `services/AGENTS.md`, same scope | rule still applies only under services |
| old build notes: run the project's test command before release | moved | matching release skill, verification step | procedure includes the original release condition |
| old note names a deleted service | obsolete | service and references confirmed absent | searched current source and entrypoints |

Allowed dispositions are retained, moved, consolidated with equivalent coverage, or obsolete with a specific reason. A file count or a generic statement that all guidance was copied is insufficient.

## Preserve the root index first

Before any installer apply or new indexing hook activation, review the existing `brain/index.md`. A legacy/custom index can contain unique policy or navigation. Preserve its exact bytes in an approved temporary or target-local backup, or verify the exact current version is recoverable from version control. A tracked file with uncommitted changes is not thereby backed up.

Move meaningful prose into appropriate topic notes, behavioral policy into an effective instruction/skill entrypoint, and curated navigation into link-only subindexes. Repair links relative to the new location. Keep all referenced content reachable. Supply `--index-reviewed` only after this review and migration. Generated inventories with no unique content need review only. Never run an indexer to discover whether the old index mattered: it would replace it.

## Choose effective destinations

- Keep scoped instructions effective in their original scope. A nested AGENTS rule moved into an optional brain note may stop applying. Preserve the nested instruction or its established loading bridge unless equivalent enforcement is verified.
- Keep root policy and useful provider compatibility entrypoints. Update their references to brain or matching skills without erasing unrelated instructions.
- Put durable repository facts, architectural decisions, and gotchas in focused brain topic notes. Use standard Markdown links relative to the containing file, including extensions.
- Put reusable procedures into matching skills after reading their current content. Activate available authoring guidance; otherwise preserve triggers, conditions, exclusions, invocation controls, and local resource closure. Do not put references to the author's repository documents into portable skills.
- Keep pending work in `brain/todos.md`, preserving existing IDs and next-id state. Activate the installed `todo` skill when migrating backlog items. Existing plans/audits belong in their matching brain directories when still relevant.
- Mark obsolete guidance only with evidence: removed component, superseded equivalent obligation, or an explicit user decision. Uncertainty remains intact and is reported for a concrete choice.

Preserve meaning rather than sentence shape. In particular, "only after approval" must not become "consider approval", and conditional instructions must not become unconditional rules. Resolve conflicting policies with the user when current authorization does not establish precedence.

For each relocated behavioral rule, compare a concrete triggering action before and after migration. Preserve its operative wording when no rewrite is needed; verify that a rewrite still covers every action to which the original applied. Matching keywords alone does not establish equivalence.

## Retire sources after proof

Review each obligation against its actual destination. Confirm links and loading paths, conditions, scope, exclusions, and approval requirements. Check that retained custom skill files work with the installed helpers. Keep the mapping concise and readable; do not dump transcripts or whole source documents into it.

Update incoming references before deleting legacy files. Remove an old ingestion/loading registration only when it belongs to the retired guidance workflow and all relevant obligations remain effective. Preserve unrelated security hooks and provider settings. Avoid creating OKF/frontmatter rules, source-ingestion automation, global tool guards, automatic semantic maintenance, or a second knowledge system.

Preserve recoverable exact content before replacement/removal, including uncommitted edits. If verification fails, restore only affected files after checking for newer user changes. Do not commit, stash, reset, or restore the whole tree automatically. Leave unresolved guidance intact and report it.

## Completion

Complete migration only when every source obligation has a verified disposition, all new brain files are reachable, incoming links work, retained rules keep their scope, and retired loaders no longer point at deleted files. Reconcile curated indexes, then use the installed brain skill's manual index command if hooks are absent. Report backup locations and any remaining decisions separately from successful mechanical installation.
