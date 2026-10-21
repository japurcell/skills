# Use standard Markdown links throughout the brain

## Purpose / Big Picture

Todo 9 replaces Obsidian note-link syntax with standard Markdown links so repository notes and generated navigation work in ordinary Markdown tools. Links must resolve relative to the file containing them, include the actual file extension, preserve explicit labels and heading fragments, and encode special destination characters. Existing note content, permanent todo IDs, hook provider envelopes and filesystem safeguards remain unchanged.

## Progress

- [x] (2026-10-21) [milestone-1] T1: Reproduce old output through copied hook processes, update canonical link rendering and existing public tests, and regenerate provider artifacts.
- [x] (2026-10-21) [milestone-2] T2: Convert existing note links and update repository/skill authoring guidance, retaining valid relative targets.
- [x] (2026-10-21) [milestone-2] T3: Verify process/generator behavior, source-wide link conversion and brain reachability; reflect, archive todo 9 and this plan.

## Surprises & Discoveries

Concurrent edits renamed the meditate prompt reference from `agents.md` to `agent-prompts.md`; this task updates the renamed file and preserves those edits. Double brackets also occur in Bash conditions, TOML table headers, regular expressions and JavaScript arrays. Those are language syntax, not note links, and must remain unchanged. The published teaching skill has two references to future teaching-workspace files; express those as workspace-relative authoring examples rather than adding broken links inside the skill bundle.

## Decision Log

On 2026-10-21, the user authorized implementing todo 9. Use the existing hook process/vault and generator seams already approved during the migration. No new test boundary is required. Update existing public expectations before changing rendering. This is a formatting migration, not permission to alter scope, providers, installation or lifecycle policies.

Use file-relative URL destinations and the current path-like labels in generated indexes. Encode destination characters with the existing standard-library URL encoder; escape label brackets/backslashes. Preserve all existing traversal bounds and handle operations. No new runtime dependency or permanent migration utility is needed.

## Outcomes & Retrospective

Todo 9 is complete. The copied-script test reproduced old output before the canonical change. All 26 process tests passed afterward with one explicit native Windows skip, and all 25 generator tests passed. The six standalone brain outputs and six build/receipt outputs were regenerated. Converted 91 resolved references in 27 brain documents and updated repository/skill authoring guidance. Standard links now cover generated and curated navigation, while indexed-directory pruning and full codebase expansion remain intact. Todo 9 and this completed plan are archived; no commit, push or global installation was performed.

## Context and Orientation

Work from `/Users/adam/.codex/worktrees/6578/skills`. Canonical root rendering is `inventory` in `hooks/families/brain.py`; generated scripts live in `.github/hooks/scripts`, `.gemini/hooks/scripts` and `.codex/hooks`. The generator also updates diagnostic/scanner build receipts. Edit canonical sources and regenerate, never hand-edit generated scripts. `scripts/test-brain-hooks.py` exercises copied scripts and provider responses. `scripts/test-generate-hooks.py` checks generation and ownership.

Human notes live in `brain/`. The hook owns `brain/index.md`; curated indexes own the other navigation files. A regular subdirectory index ends root expansion except that every Markdown file beneath `brain/codebase` remains listed. Keep that recently approved behavior.

The updated active guidance includes `AGENTS.md`, repository-local brain/reflect/meditate/ruminate/todo skills and meditate reference prompts. The teaching skill's learning-record reference now uses workspace-relative Markdown authoring examples. Other double-bracket occurrences are reviewed by language and meaning.

## Plan of Work

### Milestone 1: Generate portable Markdown navigation
Status: done
Acceptance: met

T1 has no prerequisites. Update literal expected links in the existing copied-process tests, run them against the previous generated scripts to establish a failing public reproducer, then replace the conditional link renderer with one standard Markdown path. Test ordinary, nested, Unicode and special-character filenames, oversized context fallback, unchanged timestamps and provider envelopes through the existing suite. Regenerate all provider artifacts and confirm output targets resolve to vault files.

### Milestone 2: Migrate notes and finish the backlog item
Status: done
Acceptance: met

T2 depends on T1's output contract. Resolve existing brain references using their old same-directory, relative-path and vault-root resolution rules before replacing them with explicit relative Markdown destinations. Preserve aliases and fragments. Update instructions to create file-relative links with extensions, rather than retaining a second supported note syntax.

T3 depends on T1 and T2. Run integrated public checks and one-time source/link/reachability audits. Keep archival evidence intact. Mark todo 9 complete only when these pass, preserving its permanent ID and next-id marker. Move the completed plan and backlog item to the existing archive conventions, update navigation, and run the actual indexer again. Stop after implementation and verification; committing, pushing, real global installs and unrelated backlog work are not part of this request.

## Concrete Steps

No work remains in this plan. Todo 9 is archived with its permanent ID; the completed plan lives at `brain/archive/plans/09-markdown-links/ExecPlan.md`. Existing other-session edits, including the meditate reference rename, remain preserved. Stop without starting unrelated backlog work or committing/pushing unless the user requests it.

## Validation and Acceptance

From the repository root, run `rtk python3 scripts/test-brain-hooks.py`, then `rtk python3 scripts/test-generate-hooks.py`. Serialize generator fixtures and repository edits. Expect all cases passing with explicit native Windows skips on this macOS host. Run `rtk python3 scripts/generate-hooks.py --check` expecting 60 current outputs and `rtk git diff --check` expecting no whitespace errors. Validate changed skills with the existing quick validator. One-time audits must distinguish actual note links from programming syntax, resolve every converted brain link, and traverse root/curated navigation to every brain Markdown file. No new native CI or live-provider pass is claimed for this uncommitted formatting change.

### Observed final evidence (2026-10-21)

The installed MarkdownIt CommonMark parser validated 157 local links and root-to-note reachability for all 45 brain documents after archiving. A final scan of 1,289 repository Markdown files found no double-bracket note-link syntax. The pre-conversion mapping in `/tmp/brain-todo9-conversion-map.json` retains the original 91 targets; each converted destination remains parsed as a real link, including the explicit `option value` alias. Independently copied versions of all six provider artifacts passed a one-time CommonMark check for ordinary, Unicode, bracket, fragment, space, percent and question-mark filenames. All destinations resolved to the fixture files. Root output still links to `archive/index.md` rather than expanding archived plans, and lists every codebase note.

`rtk python3 scripts/test-brain-hooks.py` passed 26 cases with one explicit Windows-only skip. `rtk python3 scripts/test-generate-hooks.py` passed 25 cases. Freshness reports 60 current outputs; whitespace checks pass. Quick validation passed the five edited repository-local skills: brain, reflect, meditate, ruminate and todo. Only the teaching skill reference text changed; its `SKILL.md` is byte-for-byte unchanged. The generic quick validator rejects its existing `argument-hint` metadata on both HEAD and the working tree. [Official Claude Code documentation](https://code.claude.com/docs/en/skills#frontmatter-reference) documents that field and explains the stricter upload/packaging schema. This is a retained host-compatibility limit, not a new link defect or a claimed validator pass. No existing metadata, test or validator was weakened.

A source-wide Markdown scan found no double-bracket note links. Remaining double brackets in non-Markdown files are language constructs, not navigation. Reflection: the uniform generator, existing public process assertions and revised brain writing contract enforce the new format structurally; no new permanent migration helper, runtime dependency or extra skill is needed.

## Idempotence and Recovery

The generator and actual indexer must converge on repeat runs without unnecessary writes. Preserve unrelated concurrent edits. Before the one-time note conversion, resolve every old reference and retain the mapping in temporary evidence; do not guess missing destinations. On an unexpected unresolved note link, leave that file unchanged until its target is established. Git tracks previous source/content; no destructive external change is needed.

## Interfaces and Dependencies

Keep the two standalone Python 3.12+ commands and all provider input/output envelopes unchanged. The root inventory remains UTF-8 Markdown with links relative to `brain/index.md`. Use only the existing Python standard library and repository validators. No new service, hook, parser framework or install-time dependency is required.
