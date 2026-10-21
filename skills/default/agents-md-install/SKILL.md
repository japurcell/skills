---
name: agents-md-install
description: Install, audit, or update root and nested AGENTS.md files and task-specific reference docs in a project.
disable-model-invocation: true
---

# AGENTS.md Install

Make the target repository teach agents how to work there. Keep shared instructions small, put scope-specific rules near their code, and route conditional work to focused documentation.

## 1. Establish scope and evidence

Use the requested project and operation. Infer the project from the current working directory when unambiguous. An explicit install or update request authorizes relevant documentation edits; an audit or proposal request is read-only. Ask only when the target, authority, or a consequential policy choice remains unresolved after inspection.

The write boundary is root and nested `AGENTS.md` files and the reference documentation needed by those files. Preserve unrelated edits. Tool-specific compatibility bridges such as `CLAUDE.md`, `GEMINI.md`, `.github/copilot-instructions.md`, custom-agent definitions, and host configuration are outside this skill's write boundary. Do not create, replace, or synchronize them. Read existing guidance as needed to avoid contradictory instructions. If a proposed AGENTS.md edit would also modify an excluded file through a symlink or shared target, report the boundary and leave that path unchanged.

Inspect before drafting:

- Read applicable ancestor instructions and inventory all project-owned root and nested AGENTS.md files, including hidden directories. Exclude dependencies, build output, vendored trees, and separate repositories unless explicitly in scope. Do not truncate the inventory; report inaccessible scopes.
- Read each in-scope instruction file and the reference docs relevant to its rules. Treat `.AGENTS.md` or other legacy names as discovery evidence, not portable auto-loaded files; preserve them unless migration is requested.
- Inspect project manifests, build and test entry points, CI, contributor docs, and representative code only far enough to verify actionable guidance and meaningful scope boundaries.
- Separate current project facts, existing policy, and proposed policy. A code pattern is evidence of implementation, not authority to invent a new mandate. Record unknowns instead of guessing commands, versions, coverage thresholds, or approval rules.

Finish discovery with a concise evidence-based assessment: missing routes, stale or contradictory guidance, duplicated rules, and the files that need changes. A numerical score and exhaustive directory tour are unnecessary. For an audit, report these findings and stop without writes.

## 2. Choose the instruction layout

Read [Placement rules](references/placement.md) before creating or reorganizing the layout. Reuse existing authoritative docs before adding new ones.

Keep in the root only the project purpose when useful, essential shared operating rules, non-obvious shared commands, cross-scope boundaries, and short routes to conditional guidance. Every retained line should change a plausible agent decision or make required context discoverable.

Create nested AGENTS.md files when a real directory scope has different commands, architecture constraints, conventions, or ownership rules. This is required when keeping those rules at the root would load unrelated instructions for other scopes. An existing package README can own the detailed procedure, but does not replace this scoped AGENTS.md entry point: create the entry point and link the relevant procedure. Do not create one per directory by habit. Keep shared rules at their common ancestor; preserve intentional local exceptions.

Put conditional topics in focused reference docs, reached through explicit task or path conditions. A pointer must identify when to read the document and what decision it governs. Keep required guidance directly reachable from the applicable AGENTS.md; avoid chains of index pages and blanket instructions to read every reference. Split because a different task needs different content, not to satisfy a line quota.

A nested guide may link its README for the general workflow, but must also link conditional policy documents directly with their task triggers. A README's migration link does not replace the migration link in the applicable AGENTS.md.

Trace the content behind each pointer, not just its label. Routing every task to a contributor guide that mixes unrelated scope rules defeats disclosure. Link to the relevant existing section, reorganize guidance into focused sections when authorized, or put the necessary concise commands and constraints directly in their scoped guide. Keep essential shared limits visible at the root rather than hiding them behind a task-specific route.

## 3. Write or reconcile

When any existing guidance will change, read [Updating existing guidance](references/update.md) first. Preserve the meaning, scope, conditions, and exceptions of valid requirements while relocating or simplifying them. Resolve policy conflicts with the user when precedence and current evidence do not settle them. Continue independent edits while that decision remains open.

Use ordinary Markdown and relative links from the containing document. Match the project's language and documentation conventions. Write exact commands with their working directory, prerequisites, and the changes that require them. Prefer a verified canonical example or source path over copied code. Explain non-obvious constraints briefly.

Document the existing validation contract: focused checks while iterating and the checks required before finishing the relevant change. Do not invent a universal full-suite requirement or weaken one the project already has. Keep secrets and private operational values out of guidance; name required environment variables without their values.

Apply the requested edits after the assessment without asking for redundant confirmation. An unresolved conflict blocks only the affected policy change. Keep generic advice, exhaustive manifests, and one-off task history out of the installed guidance. Recommend enforcement in tools when appropriate, but do not modify application code, CI, or tooling as part of this documentation task.

## 4. Verify the result

- Check every changed local link and command path from its containing file. Repair dangling links introduced by moves, including links from other in-scope docs. If an incoming link belongs to an excluded file, retain a compatible target or report the unresolved migration rather than editing that file.
- Verify commands against their actual definitions. Run relevant safe local validation when available and authorized. Do not run deployment, destructive migration, production access, or dependency-changing commands merely to test the prose. Report which commands were executed, checked statically, or could not be verified.
- Trace representative tasks through the resulting root, nested files, and references: a root-level change, each distinct affected scope, and a cross-scope change where applicable. Each trace must reach its required rules and validation without loading unrelated topic docs or losing inherited constraints.
- Compare existing requirements with the new locations and dispositions. Check retained exceptions, user edits, excluded files, and any unresolved conflicts. Repeating the operation against unchanged evidence should preserve an already adequate layout.
- Run the target's applicable documentation checks. Distinguish link/content checks from live host loading: AGENTS.md discovery and precedence vary by host. Only claim host behavior verified by a real check; do not add compatibility bridges to compensate.

Finish with changed paths, reasons for material moves or removals, validation results, and unresolved decisions or limits. If the existing layout is already adequate, leave it unchanged and say why.
