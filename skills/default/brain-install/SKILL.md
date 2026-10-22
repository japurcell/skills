---
name: brain-install
description: Install a portable brain vault, six local brain skills, and optional repository hooks, migrating existing guidance when present.
argument-hint: "[target-repository] [--provider copilot|codex|gemini ...]"
disable-model-invocation: true
compatibility: Python 3.12+; standard library only. Hooks support Copilot, Codex, and Gemini independently.
---

# Brain Install

Install into the user's explicit target repository. Resolve `<skill-path>` to this bundle's directory and `<target>` to the target's real directory path. Use an available Python 3.12+ interpreter throughout (`python`, `python3`, or `py -3.12`). Runtime resources are bundled; no downloads or global installation are needed.

## 1. Inspect the target

Read the target's applicable instructions and current worktree state. Preserve manual changes. Inventory existing root/nested guidance, memory/KB notes, linked references, relevant skills, and registrations that load guidance. Check for an existing `brain/index.md` before running any indexer or activating hooks.

Use only the requested providers. Repeat `--provider copilot`, `--provider codex`, or `--provider gemini` for any combination. Omit these options for no hooks. If the user has not requested hooks, use no hooks and say so. Selection adds or updates a provider; omission never removes a previously installed provider. User-global settings remain outside this operation.

Run inspection before applying:

```text
python <skill-path>/scripts/install.py <target> [--provider PROVIDER ...]
```

Quote paths according to the active shell or invoke with a subprocess argument list. Inspection never writes. Exit 0 is a successful inspection, 2 is a conflict or invalid input, and 1 is an application/I/O failure. Read diagnostics and affected paths before proceeding.

## 2. Preserve and reconcile

When guidance exists, read [migration procedure](references/migration.md) completely. Follow it for obligation inventory, placement, source retirement, and the target migration audit.

An existing root index is a preservation checkpoint before **any** installer writes. If it contains unique prose or curated navigation, retain its exact current bytes in a recoverable location and migrate meaningful content into topic notes or curated indexes first. Then pass `--index-reviewed`. An already generated inventory still requires review, but no backup if it has no unique content. The flag records your acknowledgement; it does not perform semantic review.

Resolve each reported content conflict concretely. Preserve existing todos, principles, notes, skills, and unrelated settings. For an eligible seed note, curated index, or skill file that should remain unchanged, repeat `--keep-existing repository/relative/path`. Verify retained skill files remain compatible with their callers. Keep choices are per invocation; repeat them on retry. Required AGENTS sections, selected provider registrations, and generated `brain/index.md` cannot be skipped this way.

For a populated codebase, plans, audits, or archive directory without an index, create a curated `index.md` linking its existing content, then retain it with `--keep-existing`. Empty starter indexes are only for empty directories.

For differing AGENTS sections or brain hook registrations, show the concrete difference and reconcile it through reviewed edits. Follow authorization already given; ask for a decision only when conflicting requirements leave a real choice. Back up exact uncommitted content before replacement. Do not add broad overwrite switches or infer permission to discard instructions.

## 3. Install

Rerun inspection with resolved options, then apply:

```text
python <skill-path>/scripts/install.py <target> [--provider PROVIDER ...] [--keep-existing PATH ...] [--index-reviewed] --apply
```

The installer creates missing starter notes and six local skills, reconciles the exact Brain and End of Work Session Defined sections in root AGENTS.md, optionally merges repository hooks, and generates the root index. Principles and their linked notes accompany the starter vault. The always-installed brain skill includes manual indexing instructions for repositories without hooks.

Continue any remaining semantic migration after mechanical installation. Activate the installed `brain` skill for vault edits. Activate matching skill-authoring guidance when revising other skills; if unavailable, preserve their triggers and invocation controls, keep resources self-contained, and verify their procedures directly. Use a short checklist if planning tools are unavailable. Do not automatically activate `meditate` or `ruminate`.

## 4. Verify and report

- Inspect installed files, the two AGENTS sections, curated navigation, and generated `brain/index.md`. Every new brain note must be reachable. Confirm the empty starter backlog did not replace an existing backlog.
- Reconcile the obligation audit with actual destinations, conditions, scope, exclusions, approvals, and legacy reference repairs. Retire old guidance/loading hooks only after this proof.
- Exercise the installed manual indexer using its documented JSON-stdin command. Inspect stderr and expected index links; the hooks' zero exit code alone does not prove success.
- Inspect selected hook registrations and run their commands with representative provider input where possible. Preserve unrelated handlers, unselected providers, and global configuration. Provider trust review remains a native provider action; do not bypass it.
- Repeat inspection with the same choices, including index acknowledgement after reviewing its current contents. Identical files should remain unchanged. Report retained custom files and any compatibility limits.

Report installed paths, selected providers, migrated/retained/obsolete obligations, checks run, unresolved conflicts, and recoverable source locations. Distinguish local subprocess checks, native operating-system checks, and live-provider context delivery. Claim only observed results. A partial I/O failure lists completed paths; resolve its cause and retry without resetting the target or deleting an active index lock.
