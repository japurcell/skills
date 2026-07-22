# Payload Parser Patterns

Use when editing path extraction, file classification, or parser tests.

## Core Rules

- Parse paths from hook `stdin` before using worktree fallbacks.
- Support both common payload styles when the repo already does or should:
  - camelCase: `toolArgs`, `toolName`, `filePath`
  - snake_case: `tool_input`, `tool_name`, `file_path`
- Support `apply_patch` paths from:
  1. object
  2. stringified object
  3. raw patch text
- Normalize and deduplicate before scope filtering.
- Reject or ignore absolute paths and paths containing `..` unless safely normalized under repo root.
- Keep GitHub and Gemini parser and file-classification behavior equivalent unless documenting an exception.

These examples assume `jq` is available. If `jq` is missing, hooks should fail open or use a documented fallback path, but must still emit valid response JSON.

## Direct Path Extraction

Adapt this baseline:

```bash
extract_paths_from_payload() {
  local input_json="$1"

  printf '%s' "$input_json" | jq -r '
    def arg_objects:
      [.toolArgs?, .tool_input?]
      | map(select(type == "object"))
      | .[];

    [
      arg_objects.filePath?,
      arg_objects.file_path?,
      arg_objects.path?,
      arg_objects.paths[]?,
      arg_objects.files[]?
    ]
    | .[]
    | select(type == "string" and length > 0)
  '
}
```

## `apply_patch` Path Extraction

Adapt this baseline:

```bash
extract_patch_paths_from_payload() {
  local input_json="$1"

  printf '%s' "$input_json" | jq -r '
    def maybe_fromjson:
      if type == "string" then try fromjson catch . else . end;

    def arg_objects:
      [.toolArgs?, .tool_input?]
      | map(select(type == "object"))
      | .[];

    def patch_candidates:
      [arg_objects.patch?, arg_objects.input?, arg_objects.content?]
      | .[]
      | maybe_fromjson;

    def patch_texts:
      patch_candidates
      | if type == "object" then
          [.patch?, .input?, .content?, .text?]
          | .[]
          | select(type == "string")
        elif type == "string" then
          .
        else
          empty
        end;

    patch_texts
    | scan("(?m)^(?:\\+\\+\\+ b/|--- a/|diff --git a/[^ ]+ b/|\\*\\*\\* Update File: |\\*\\*\\* Add File: |\\*\\*\\* Delete File: )([^\\n\\t ]+)")
  '
}
```

## Regression Fixture Minimums

When parser behavior changes, include focused fixtures for:

- `write_file` with `toolArgs.filePath`
- `write_file` with `tool_input.file_path`
- `replace` with `toolArgs.filePath`
- `replace` with `tool_input.file_path`
- `apply_patch` object
- `apply_patch` stringified object
- `apply_patch` raw string
- missing/empty payload paths causing fallback behavior

Minimal examples:

```json
{"event":"postToolUse","toolName":"write_file","toolArgs":{"filePath":"src/example.ts","content":"x"}}
```

```json
{"event":"PostToolUse","tool_name":"write_file","tool_input":{"file_path":"src/example.ts","content":"x"}}
```

```json
{"event":"postToolUse","toolName":"replace","toolArgs":{"filePath":"src/example.ts","oldString":"a","newString":"b"}}
```

```json
{"event":"PostToolUse","tool_name":"replace","tool_input":{"file_path":"src/example.ts","old_string":"a","new_string":"b"}}
```

```json
{"event":"postToolUse","toolName":"apply_patch","toolArgs":{"patch":{"content":"*** Begin Patch\n*** Update File: src/example.ts\n@@\n-a\n+b\n*** End Patch\n"}}}
```

```json
{"event":"postToolUse","toolName":"apply_patch","toolArgs":{"patch":"{\"content\":\"*** Begin Patch\\n*** Update File: src/example.ts\\n@@\\n-a\\n+b\\n*** End Patch\\n\"}"}}
```

```json
{"event":"postToolUse","toolName":"apply_patch","toolArgs":{"patch":"*** Begin Patch\n*** Update File: src/example.ts\n@@\n-a\n+b\n*** End Patch\n"}}
```

Expected path for each example:

```text
src/example.ts
```
