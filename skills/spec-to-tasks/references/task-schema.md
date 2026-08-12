# tasks.json schema

The saved file must be valid JSON only.

```json
{
  "project": "Project Name",
  "branchName": "feature-name-kebab-case",
  "description": "Short feature description",
  "tasks": [
    {
      "id": "T001",
      "parentStoryId": "US-001",
      "title": "Small implementation task title",
      "description": "Scope, verification, context, and mapped requirement IDs.",
      "acceptanceCriteria": [
        "Concrete, testable behavior",
        "Typecheck passes"
      ],
      "filesLikelyTouched": [
        "src/path/file.ts"
      ],
      "designGuidance": [
        {
          "source": "doc, pattern, or decision",
          "description": "Guidance",
          "rationale": "Why it matters"
        }
      ],
      "priority": 1,
      "passes": false,
      "notes": ""
    }
  ]
}
```

## Top-level fields

- `project`: project or feature name.
- `branchName`: kebab-case feature name.
- `description`: short feature summary.
- `tasks`: ordered task list.

## Task fields

- `id`: sequential IDs: `T001`, `T002`, ...
- `parentStoryId`: existing story ID, or stable synthesized ID such as `US-001`.
- `title`: short implementation task title.
- `description`: scope, verification, context, and mapped requirement IDs.
- `acceptanceCriteria`: concrete, testable criteria.
- `filesLikelyTouched`: confidently inferable paths; otherwise `[]`.
- `designGuidance`: useful guidance only; otherwise `[]`.
- `priority`: unique ascending integer.
- `passes`: always `false`.
- `notes`: always `""`.
