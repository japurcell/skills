# Payload Parser Patterns

Use when editing path extraction, file classification, or parser tests.

Rules:

- Parse paths from hook `stdin` before worktree fallback.
- Support the repo’s expected payload styles:
  - camelCase: `toolArgs`, `toolName`, `filePath`
  - snake_case: `tool_input`, `tool_name`, `file_path`
- Support `apply_patch` as:
  1. object
  2. stringified object
  3. raw patch text
- Normalize, dedupe, then scope-filter.
- Reject/ignore absolute paths and `..` paths unless safely normalized under repo root.
- Keep GitHub and Gemini parser/classifier behavior equivalent unless documenting an exception.
- Malformed or missing payload paths may trigger fallback detection.
- Never silently discard valid payload paths.
- Parser failures usually fail open for formatter/verifier hooks unless repo policy requires blocking.

## Direct Paths

Candidate argument objects:

```text
payload.toolArgs
payload.tool_input
```

Candidate fields:

```text
filePath
file_path
path
paths[]
files[]
```

Algorithm:

```text
paths = []

for arg in [payload.toolArgs, payload.tool_input]:
  if arg is not object: continue

  for field in [filePath, file_path, path]:
    if arg[field] is non-empty string:
      paths.append(arg[field])

  for field in [paths, files]:
    if arg[field] is array:
      append non-empty string items

paths = normalize_under_repo_root(paths)
paths = dedupe_preserving_order(paths)
return paths
```

## `apply_patch` Paths

Candidate patch fields:

```text
patch
input
content
```

If a string appears to contain JSON, try parsing it. If parsing fails, treat it as raw text.

If a candidate is an object, inspect string fields:

```text
patch
input
content
text
```

Extract paths from common raw patch markers:

```text
+++ b/<path>
--- a/<path>
diff --git a/<old> b/<new>
*** Update File: <path>
*** Add File: <path>
*** Delete File: <path>
```

Algorithm:

```text
patch_texts = []

for arg in [payload.toolArgs, payload.tool_input]:
  if arg is not object: continue

  for field in [patch, input, content]:
    candidate = arg[field]

    if candidate is string:
      parsed = try_parse_json(candidate)
      if parsed succeeds:
        candidate = parsed
      else:
        patch_texts.append(candidate)
        continue

    if candidate is object:
      for text_field in [patch, input, content, text]:
        if candidate[text_field] is string:
          patch_texts.append(candidate[text_field])

for text in patch_texts:
  extract paths from supported patch markers

paths = normalize_under_repo_root(paths)
paths = dedupe_preserving_order(paths)
return paths
```

## Normalization

- Convert separators as needed.
- Prefer repo-relative paths.
- Reject/ignore paths that escape repo root after normalization.
- Preserve stable order for deterministic tests.

## Minimum Parser Fixtures

When parser behavior changes, test:

- `write_file` with `toolArgs.filePath`
- `write_file` with `tool_input.file_path`
- `replace` with `toolArgs.filePath`
- `replace` with `tool_input.file_path`
- `apply_patch` object
- `apply_patch` stringified object
- `apply_patch` raw text
- missing/empty payload paths causing fallback behavior

Compact examples; each should produce `src/example.ts`:

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
