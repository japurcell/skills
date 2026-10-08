# tasks.json schema

## Contents

- [Complete example](#complete-example)
- [Top-level fields](#top-level-fields)
- [Existing task fields](#existing-task-fields)
- [Enriched task fields](#enriched-task-fields)
- [Task types](#task-types)
- [Verification checks](#verification-checks)

The saved file must be valid JSON only. Each task must use all existing task fields and the complete enriched contract.

## Complete example

This synthetic documentation task demonstrates a complete enriched record with inline source/context, a verified typecheck classification, and a required manual check. Its paths and requirement labels illustrate the format; use real source material and paths from the actual input when generating a manifest.

```json
{
  "project": "Example project",
  "branchName": "document-private-install-refusal",
  "description": "Document private-install refusal behavior",
  "tasks": [
    {
      "id": "T001",
      "parentStoryId": "US-001",
      "title": "Document private-install refusal behavior",
      "description": "Update the private-install guide to explain the no-write refusal boundary and the metadata that must be preserved.",
      "acceptanceCriteria": [
        "The guide states that a conflicting existing destination is refused before writes.",
        "The guide identifies the Git metadata and indexes that remain unchanged."
      ],
      "filesLikelyTouched": [
        "docs/private-install.md"
      ],
      "designGuidance": [],
      "priority": 1,
      "passes": false,
      "notes": "",
      "dependsOn": [],
      "sourceRefs": [
        {
          "path": null,
          "section": null,
          "requirements": ["REQ-REFUSAL"],
          "content": "REQ-REFUSAL: A conflicting existing destination is refused before any destination writes."
        }
      ],
      "requiredContext": [
        {
          "path": null,
          "section": null,
          "purpose": "Preserve the current metadata and no-write boundary when editing the guide.",
          "content": "Current contract: private installation preserves tracked files and both Git indexes; conflicts cause refusal without destination writes."
        }
      ],
      "taskType": "documentation",
      "verification": [
        {
          "id": "typecheck",
          "kind": "typecheck",
          "applicability": "not-applicable",
          "command": null,
          "workingDirectory": ".",
          "expected": "The verified documentation-only scope contains no executable source or type declarations.",
          "reason": "Only the guide is in scope, so a typecheck does not apply."
        },
        {
          "id": "guide-review",
          "kind": "manual",
          "applicability": "required",
          "command": null,
          "workingDirectory": ".",
          "expected": "Procedure: compare the guide with REQ-REFUSAL and the inline current contract. Evidence: the review confirms both refusal-before-write and metadata-preservation statements are present and accurate.",
          "reason": "The required outcome is the accuracy of user-facing documentation."
        }
      ]
    }
  ]
}
```

## Top-level fields

- `project`: project or feature name.
- `branchName`: kebab-case feature name.
- `description`: short feature summary.
- `tasks`: ordered task list.

Keep these existing fields when updating a manifest.

## Existing task fields

Preserve these fields and their meanings:

- `id`: sequential `T001`, `T002`, ... for a new manifest. Preserve existing IDs when updating a manifest.
- `parentStoryId`: an existing story ID or stable synthesized ID such as `US-001`.
- `title`: short task outcome.
- `description`: bounded scope, relevant context, mapped requirements, and any reasoning risks or bounded entry points.
- `acceptanceCriteria`: concrete behavior or evidence that establishes the task outcome. Do not require the literal `Typecheck passes` for every task.
- `filesLikelyTouched`: confidently inferable repository-relative paths; use `[]` when none can be inferred.
- `designGuidance`: useful decisions or patterns, each with `source`, `description`, and `rationale`; use `[]` when none is needed.
- `priority`: unique ascending integer. It records task ordering, not permission to bypass prerequisites.
- `passes`: `false` for every new task. Preserve the current value and its evidence when updating an existing manifest.
- `notes`: `""` for every new task. Preserve existing notes and completion evidence during an update.

## Enriched task fields

Every task must include all five fields below. A task missing any of them is incomplete.

- `dependsOn`: array of prerequisite task ID strings. Use `[]` when there are no prerequisites. A dependent task is eligible only after every listed prerequisite passes. Every edge must point to a real task, avoid self and duplicate edges, and participate in an acyclic graph. Preserve mandatory source order with explicit edges. Do not infer edges from IDs or priority alone.
- `sourceRefs`: nonempty array identifying the source sections and requirements implemented or verified by this task. Every object has `path`, `section`, and `requirements`. For a file reference, `path` is a nonempty repository-relative string and `section` is a nonempty section name. Use stable current-contract headings or requirement IDs when available, and update affected references when the source changes. Each requirement label must resolve to source content. For inline source, set both `path` and `section` to `null` and include nonempty `content` with the relevant original input. Never set only one of `path` and `section` to `null`; do not invent a source path or requirement.
- `requiredContext`: array naming the exact design or policy context the worker must read. Each object has `path`, `section`, and `purpose`. For a file reference, `path` is a nonempty repository-relative string and `section` is a nonempty section name. Include inherited invariants that constrain the task; do not point every task at the whole spec by default. An empty array is valid only when the task and manifest already contain all context needed to complete it. For inline context, set both `path` and `section` to `null` and include nonempty `content`. Never set only one of `path` and `section` to `null`.
- `taskType`: one of `decision`, `implementation`, `verification`, `integration`, or `documentation`. The type identifies the primary outcome; it does not excuse an independently valueless horizontal fragment.
- `verification`: array of check objects. Every task has at least one `required` check that directly establishes its outcome, plus an explicit `typecheck` check classified as `required`, `not-applicable`, or `unresolved` and checks for other relevant categories. Checks describe expected work, not evidence that it has passed.

Paths in `sourceRefs`, `requiredContext`, and `verification.workingDirectory` are repository-relative. When source or context lives outside the repository or only in the conversation, use the inline form instead of an absolute path. A source reference and a context reference may point to the same material, but they serve different purposes: one maps requirements, and one tells the worker what to read and why.

## Task types

- `decision`: resolve a named uncertainty within the task's authority and record the decision, evidence, and boundary. If user approval is required, stop and request it instead.
- `implementation`: deliver the behavior, including the layers and negative cases required for a complete vertical slice.
- `verification`: collect specified, reproducible evidence without implying that unverified behavior passed.
- `integration`: prove that contributing tasks compose correctly and preserve shared invariants.
- `documentation`: reconcile instructions or claims against the current source contract and verify their accuracy.

Each type needs a concrete outcome, relevant source references, sufficient context, and applicable verification.

## Verification checks

Each check object has exactly these fields:

- `id`: stable, nonempty identifier unique within the task.
- `kind`: one of `test`, `typecheck`, `build`, `lint`, or `manual`.
- `applicability`: `required`, `not-applicable`, or `unresolved`.
- `command`: a known command string, or `null` for a manual or not-applicable check, or when a required command is not yet known. An unresolved check keeps a known command if its blocker is host or access availability.
- `workingDirectory`: repository-relative directory, such as `.`.
- `expected`: observable result. For required manual checks, include both the procedure and the expected evidence.
- `reason`: why the check applies, does not apply, or remains unresolved.

For a required automated check, name the known command and the observable result before execution. For a required manual check, use `command: null` and describe a concrete procedure and expected evidence in `expected`. For a not-applicable check, use `command: null` and give a verified reason. For an unresolved check, state what must be discovered and keep the task unready. Use `command: null` only when the command is unknown; retain a known command when host or access availability blocks execution. No check object is proof of a pass; only later execution evidence can establish that.

Never invent or erase a command, or reclassify a known failing applicable check as inapplicable. A task may discover an unknown verification procedure as its own bounded deliverable, but that discovery does not prove the product behavior awaiting the procedure. Keep the dependent behavior's verification unresolved until an applicable procedure and evidence exist.
