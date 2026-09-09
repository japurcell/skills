#!/usr/bin/env bash

set -euo pipefail

source "$(dirname "${BASH_SOURCE[0]}")/test-common.sh"

readonly FIXTURE_ROOT="$REPO_ROOT/scripts/fixtures/okf-valid-repo"
readonly LINTER_PATH="$REPO_ROOT/scripts/lint-okf.py"
readonly VENDOR_SOURCE="$REPO_ROOT/scripts/vendor/PyYAML-6.0.3.SOURCE"
readonly VENDOR_LICENSE="$REPO_ROOT/scripts/vendor/PyYAML-6.0.3.LICENSE"
readonly VENDOR_VERSION="6.0.3"
readonly VENDOR_URL="https://files.pythonhosted.org/packages/05/8e/961c0007c59b8dd7729d542c61a4d537767a59645b82a0b521206e1e25c2/pyyaml-6.0.3.tar.gz"
readonly VENDOR_SHA256="d76623373421df22fb4cf8817020cbb7ef15c725b9d5e45f17e189bfc384190f"

TEST_ROOT=""
LAST_OUTPUT=""
LAST_ERROR=""
LAST_STATUS=0

fail() {
  echo "FAILED: $*" >&2
  exit 1
}

validate_fixture_setup() {
  local reserved_paths

  [[ -d "$FIXTURE_ROOT/.agents/instructions" ]] || fail "fixture instruction bundle is missing"
  [[ -d "$FIXTURE_ROOT/.agents/memory" ]] || fail "fixture memory bundle is missing"
  [[ -f "$FIXTURE_ROOT/.agents/sources/example.md" ]] || fail "fixture raw source is missing"
  [[ -f "$FIXTURE_ROOT/.agents/memory/sources/source-ingest-manifest.json" ]] || \
    fail "fixture source-ingest manifest is missing"
  [[ -f "$FIXTURE_ROOT/README.md" ]] || fail "fixture repository-level link target is missing"
  [[ -f "$FIXTURE_ROOT/assets/diagram.svg" ]] || fail "fixture image target is missing"

  reserved_paths="$(
    find "$FIXTURE_ROOT/.agents/instructions" "$FIXTURE_ROOT/.agents/memory" \
      -type f \( -name index.md -o -name log.md \) -print
  )"
  [[ -z "$reserved_paths" ]] || fail "valid fixture contains a lowercase reserved path: $reserved_paths"

  python3 - "$FIXTURE_ROOT" <<'PY'
import hashlib
import json
from pathlib import Path
import sys

root = Path(sys.argv[1])
manifest_path = root / ".agents/memory/sources/source-ingest-manifest.json"
with manifest_path.open(encoding="utf-8") as stream:
    manifest = json.load(stream)
assert manifest["version"] == 1
assert {
    (entry["source_path"], entry["summary_path"])
    for entry in manifest["entries"]
} == {
    ("example.md", "example-md.summary.md"),
    ("pending.md", "pending-md.summary.md"),
}
for entry in manifest["entries"]:
    source = root / ".agents/sources" / entry["source_path"]
    summary = root / ".agents/memory/sources" / entry["summary_path"]
    assert source.is_file()
    assert summary.is_file()
    assert entry["size"] == source.stat().st_size
    assert entry["content_hash"] == hashlib.sha256(source.read_bytes()).hexdigest()
    assert entry["summary_hash"] == hashlib.sha256(summary.read_bytes()).hexdigest()
PY

  for expected_type in \
    "Agent Instruction" \
    "Agent Memory" \
    "Knowledge Index" \
    "Source Ingestion Log" \
    "Known Issue" \
    "Testing Guidance" \
    "Architecture Decision" \
    "Source Summary"; do
    grep -R -Fq "type: $expected_type" \
      "$FIXTURE_ROOT/.agents/instructions" "$FIXTURE_ROOT/.agents/memory" || \
      fail "valid fixture does not exercise type: $expected_type"
  done
}

assert_vendor_record() {
  [[ -s "$VENDOR_LICENSE" ]] || fail "vendored PyYAML license is missing or empty"
  [[ -f "$VENDOR_SOURCE" ]] || fail "vendored PyYAML source record is missing"
  assert_file_contains "$VENDOR_SOURCE" "$VENDOR_VERSION" "Vendor record must pin PyYAML 6.0.3."
  assert_file_contains "$VENDOR_SOURCE" "$VENDOR_URL" "Vendor record must name the accepted source URL."
  assert_file_contains "$VENDOR_SOURCE" "$VENDOR_SHA256" "Vendor record must name the accepted source hash."
}

new_case_repo() {
  local name="$1"
  local case_repo

  case_repo="$(mktemp -d "$TEST_ROOT/$name.XXXXXX")"
  cp -R "$FIXTURE_ROOT/." "$case_repo/"
  printf '%s' "$case_repo"
}

run_linter() {
  local case_repo="$1"
  shift

  if (cd "$case_repo" && "$LINTER_PATH" "$@") \
    >"$TEST_ROOT/linter.stdout" 2>"$TEST_ROOT/linter.stderr"; then
    LAST_STATUS=0
  else
    LAST_STATUS=$?
  fi
  LAST_OUTPUT="$(<"$TEST_ROOT/linter.stdout")"
  LAST_ERROR="$(<"$TEST_ROOT/linter.stderr")"
}

run_linter_path() {
  local case_repo="$1"
  local linter_path="$2"
  shift 2

  if (cd "$case_repo" && "$linter_path" "$@") \
    >"$TEST_ROOT/linter.stdout" 2>"$TEST_ROOT/linter.stderr"; then
    LAST_STATUS=0
  else
    LAST_STATUS=$?
  fi
  LAST_OUTPUT="$(<"$TEST_ROOT/linter.stdout")"
  LAST_ERROR="$(<"$TEST_ROOT/linter.stderr")"
}

assert_status() {
  local expected="$1"
  [[ "$LAST_STATUS" -eq "$expected" ]] || \
    fail "expected exit $expected, got $LAST_STATUS; stdout: $LAST_OUTPUT; stderr: $LAST_ERROR"
  [[ -z "$LAST_ERROR" ]] || fail "linter wrote unexpected stderr: $LAST_ERROR"
}

assert_json_envelope() {
  JSON_TEXT="$LAST_OUTPUT" python3 - <<'PY'
import json
import os

payload = json.loads(os.environ["JSON_TEXT"])
assert set(payload) == {"schema_version", "diagnostics"}, payload
assert payload["schema_version"] == 1, payload
assert isinstance(payload["diagnostics"], list), payload
for diagnostic in payload["diagnostics"]:
    assert set(diagnostic) == {"id", "path", "line", "column", "message"}, diagnostic
    assert isinstance(diagnostic["id"], str) and diagnostic["id"], diagnostic
    assert isinstance(diagnostic["path"], str) and diagnostic["path"], diagnostic
    assert isinstance(diagnostic["line"], int) and diagnostic["line"] >= 1, diagnostic
    assert isinstance(diagnostic["column"], int) and diagnostic["column"] >= 1, diagnostic
    assert isinstance(diagnostic["message"], str) and diagnostic["message"], diagnostic
PY
}

assert_json_clean() {
  JSON_TEXT="$LAST_OUTPUT" python3 - <<'PY'
import json
import os

assert json.loads(os.environ["JSON_TEXT"]) == {"schema_version": 1, "diagnostics": []}
PY
}

assert_json_has() {
  local expected_id="$1"
  local expected_path="$2"
  local expected_line="${3:-}"
  local expected_column="${4:-}"

  JSON_TEXT="$LAST_OUTPUT" \
    EXPECTED_ID="$expected_id" \
    EXPECTED_PATH="$expected_path" \
    EXPECTED_LINE="$expected_line" \
    EXPECTED_COLUMN="$expected_column" \
    python3 - <<'PY'
import json
import os

payload = json.loads(os.environ["JSON_TEXT"])
matches = [
    item
    for item in payload["diagnostics"]
    if item["id"] == os.environ["EXPECTED_ID"]
    and item["path"] == os.environ["EXPECTED_PATH"]
]
assert matches, payload
if os.environ["EXPECTED_LINE"]:
    assert matches[0]["line"] == int(os.environ["EXPECTED_LINE"]), matches[0]
if os.environ["EXPECTED_COLUMN"]:
    assert matches[0]["column"] == int(os.environ["EXPECTED_COLUMN"]), matches[0]
PY
}

assert_json_only_id() {
  local expected_id="$1"

  JSON_TEXT="$LAST_OUTPUT" EXPECTED_ID="$expected_id" python3 - <<'PY'
import json
import os

diagnostics = json.loads(os.environ["JSON_TEXT"])["diagnostics"]
assert diagnostics, diagnostics
assert {item["id"] for item in diagnostics} == {os.environ["EXPECTED_ID"]}, diagnostics
PY
}

assert_json_diagnostic_count() {
  local expected="$1"

  JSON_TEXT="$LAST_OUTPUT" EXPECTED_COUNT="$expected" python3 - <<'PY'
import json
import os

diagnostics = json.loads(os.environ["JSON_TEXT"])["diagnostics"]
assert len(diagnostics) == int(os.environ["EXPECTED_COUNT"]), diagnostics
PY
}

assert_json_has_id() {
  local expected_id="$1"

  JSON_TEXT="$LAST_OUTPUT" EXPECTED_ID="$expected_id" python3 - <<'PY'
import json
import os

diagnostics = json.loads(os.environ["JSON_TEXT"])["diagnostics"]
assert any(item["id"] == os.environ["EXPECTED_ID"] for item in diagnostics), diagnostics
PY
}

assert_json_sorted() {
  JSON_TEXT="$LAST_OUTPUT" python3 - <<'PY'
import json
import os

diagnostics = json.loads(os.environ["JSON_TEXT"])["diagnostics"]
expected = sorted(
    diagnostics,
    key=lambda item: (item["path"], item["line"], item["column"], item["id"]),
)
assert diagnostics == expected, diagnostics
PY
}

assert_human_json_parity() {
  local case_repo="$1"
  local human_output
  local human_error
  local human_status
  local json_output
  local json_error
  local json_status
  local rendered

  run_linter "$case_repo"
  human_output="$LAST_OUTPUT"
  human_error="$LAST_ERROR"
  human_status="$LAST_STATUS"
  run_linter "$case_repo" --format json
  json_output="$LAST_OUTPUT"
  json_error="$LAST_ERROR"
  json_status="$LAST_STATUS"

  [[ "$human_status" -eq "$json_status" ]] || fail "human and JSON exit codes differ"
  [[ -z "$human_error" ]] || fail "human mode wrote unexpected stderr: $human_error"
  [[ -z "$json_error" ]] || fail "JSON mode wrote unexpected stderr: $json_error"
  rendered="$(JSON_TEXT="$json_output" python3 - <<'PY'
import json
import os

for item in json.loads(os.environ["JSON_TEXT"])["diagnostics"]:
    print(f'{item["path"]}:{item["line"]}:{item["column"]}: {item["id"]} {item["message"]}')
PY
)"
  [[ "$human_output" == "$rendered" ]] || fail "human and JSON diagnostics differ"
}

write_concept() {
  local path="$1"
  local frontmatter="$2"

  printf '%s\n' '---' "$frontmatter" '---' '' '# Mutated concept' >"$path"
}

expect_diagnostic() {
  local case_repo="$1"
  local diagnostic_id="$2"
  local path="$3"
  local line="${4:-}"
  local column="${5:-}"

  run_linter "$case_repo" --format json
  assert_status 1
  assert_json_envelope
  assert_json_has "$diagnostic_id" "$path" "$line" "$column"
}

test_valid_corpus_and_public_output_contract() {
  local case_repo

  case_repo="$(new_case_repo valid-corpus)"
  run_linter "$case_repo"
  assert_status 0

  run_linter "$case_repo" --format json
  assert_status 0
  assert_json_envelope
  assert_json_clean
  echo "PASSED: valid corpus, all derived types, metadata, links, ignored links, and unknown fields"
}

test_okf001_non_utf8() {
  local case_repo
  case_repo="$(new_case_repo okf001-non-utf8)"
  printf '\377' >"$case_repo/.agents/memory/DRAFT.md"
  expect_diagnostic "$case_repo" OKF001 .agents/memory/DRAFT.md 1 1
  assert_json_only_id OKF001
}

test_okf002_frontmatter_delimiters() {
  local case_repo
  case_repo="$(new_case_repo okf002-missing-opening)"
  printf '%s\n' '# No frontmatter' >"$case_repo/.agents/memory/DRAFT.md"
  expect_diagnostic "$case_repo" OKF002 .agents/memory/DRAFT.md 1 1
  assert_json_only_id OKF002

  case_repo="$(new_case_repo okf002-missing-closing)"
  printf '%s\n' '---' 'type: Agent Memory' 'description: Missing close' >"$case_repo/.agents/memory/DRAFT.md"
  expect_diagnostic "$case_repo" OKF002 .agents/memory/DRAFT.md 1 1
  assert_json_only_id OKF002
}

test_okf003_yaml() {
  local case_repo
  case_repo="$(new_case_repo okf003-invalid-yaml)"
  write_concept "$case_repo/.agents/memory/DRAFT.md" $'type: [\ndescription: Invalid YAML'
  expect_diagnostic "$case_repo" OKF003 .agents/memory/DRAFT.md
  assert_json_only_id OKF003

  case_repo="$(new_case_repo okf003-non-mapping)"
  write_concept "$case_repo/.agents/memory/DRAFT.md" '- list item'
  expect_diagnostic "$case_repo" OKF003 .agents/memory/DRAFT.md 1 1
  assert_json_only_id OKF003
}

test_okf004_required_fields() {
  local case_repo
  local entry
  local name
  local cases=(
    'missing-type|description: Missing type'
    'empty-type|type: ""\ndescription: Empty type'
    'non-string-type|type: 42\ndescription: Non-string type'
    'missing-description|type: Agent Memory'
    'empty-description|type: Agent Memory\ndescription: ""'
    'non-string-description|type: Agent Memory\ndescription: 42'
  )

  for entry in "${cases[@]}"; do
    name="${entry%%|*}"
    case_repo="$(new_case_repo "okf004-$name")"
    write_concept "$case_repo/.agents/memory/DRAFT.md" "$(printf '%b' "${entry#*|}")"
    expect_diagnostic "$case_repo" OKF004 .agents/memory/DRAFT.md
  done
}

test_okf005_standard_metadata_shapes() {
  local name
  local frontmatter
  local case_repo
  local cases=(
    'title-type|type: Agent Memory\ndescription: Invalid title\ntitle: 1'
    'title-empty|type: Agent Memory\ndescription: Invalid title\ntitle: ""'
    'resource-type|type: Agent Memory\ndescription: Invalid resource\nresource: []'
    'resource-empty|type: Agent Memory\ndescription: Invalid resource\nresource: ""'
    'tags-container|type: Agent Memory\ndescription: Invalid tags\ntags: fixture'
    'tags-item|type: Agent Memory\ndescription: Invalid tags\ntags:\n  - ""'
    'sources-container|type: Agent Memory\ndescription: Invalid sources\nsources: fixture'
    'source-entry-container|type: Agent Memory\ndescription: Invalid source entry\nsources:\n  - fixture'
    'source-resource-missing|type: Agent Memory\ndescription: Invalid source entry\nsources:\n  - title: Missing resource'
    'source-resource-empty|type: Agent Memory\ndescription: Invalid source entry\nsources:\n  - resource: ""'
    'source-resource-type|type: Agent Memory\ndescription: Invalid source entry\nsources:\n  - resource: []'
    'source-id-empty|type: Agent Memory\ndescription: Invalid source id\nsources:\n  - resource: https://example.com\n    id: ""'
    'source-id-type|type: Agent Memory\ndescription: Invalid source id\nsources:\n  - resource: https://example.com\n    id: 1'
    'source-title-empty|type: Agent Memory\ndescription: Invalid source title\nsources:\n  - resource: https://example.com\n    title: ""'
    'source-title-type|type: Agent Memory\ndescription: Invalid source title\nsources:\n  - resource: https://example.com\n    title: 1'
    'source-author-empty|type: Agent Memory\ndescription: Invalid source author\nsources:\n  - resource: https://example.com\n    author: ""'
    'source-author-type|type: Agent Memory\ndescription: Invalid source author\nsources:\n  - resource: https://example.com\n    author: []'
    'source-usage-count-negative|type: Agent Memory\ndescription: Invalid usage count\nsources:\n  - resource: https://example.com\n    usage_count: -1'
    'source-usage-count-boolean|type: Agent Memory\ndescription: Invalid usage count\nsources:\n  - resource: https://example.com\n    usage_count: true'
    'source-usage-count-number|type: Agent Memory\ndescription: Invalid usage count\nsources:\n  - resource: https://example.com\n    usage_count: 1.5'
    'source-usage-window|type: Agent Memory\ndescription: Invalid source window\nsources:\n  - resource: https://example.com\n    usage_window: fixture'
    'source-usage-window-endpoint|type: Agent Memory\ndescription: Invalid source window\nsources:\n  - resource: https://example.com\n    usage_window:\n      from: 2026-09-09T00:00:00Z'
    'generated-container|type: Agent Memory\ndescription: Invalid generated\ngenerated: fixture'
    'generated-by|type: Agent Memory\ndescription: Invalid generated\ngenerated:\n  at: 2026-09-09T00:00:00Z'
    'generated-by-empty|type: Agent Memory\ndescription: Invalid generated\ngenerated:\n  by: ""\n  at: 2026-09-09T00:00:00Z'
    'generated-by-type|type: Agent Memory\ndescription: Invalid generated\ngenerated:\n  by: []\n  at: 2026-09-09T00:00:00Z'
    'generated-at|type: Agent Memory\ndescription: Invalid generated\ngenerated:\n  by: fixture'
    'verified-container|type: Agent Memory\ndescription: Invalid verified\nverified:\n  by: fixture\n  at: 2026-09-09T00:00:00Z'
    'verified-entry|type: Agent Memory\ndescription: Invalid verified\nverified:\n  - fixture'
    'verified-by|type: Agent Memory\ndescription: Invalid verified\nverified:\n  - at: 2026-09-09T00:00:00Z'
    'verified-by-empty|type: Agent Memory\ndescription: Invalid verified\nverified:\n  - by: ""\n    at: 2026-09-09T00:00:00Z'
    'verified-by-type|type: Agent Memory\ndescription: Invalid verified\nverified:\n  - by: []\n    at: 2026-09-09T00:00:00Z'
    'verified-at|type: Agent Memory\ndescription: Invalid verified\nverified:\n  - by: fixture'
    'usage-window-container|type: Agent Memory\ndescription: Invalid usage window\nusage_window: fixture'
    'usage-window-endpoint|type: Agent Memory\ndescription: Invalid usage window\nusage_window:\n  from: 2026-09-09T00:00:00Z'
    'stale-after-type|type: Agent Memory\ndescription: Invalid stale after\nstale_after: []'
    'status|type: Agent Memory\ndescription: Invalid status\nstatus: experimental'
  )

  for entry in "${cases[@]}"; do
    name="${entry%%|*}"
    frontmatter="${entry#*|}"
    case_repo="$(new_case_repo "okf005-$name")"
    write_concept "$case_repo/.agents/memory/DRAFT.md" "$(printf '%b' "$frontmatter")"
    expect_diagnostic "$case_repo" OKF005 .agents/memory/DRAFT.md
  done
}

test_okf005_non_scalar_status() {
  local case_repo

  case_repo="$(new_case_repo okf005-list-status)"
  write_concept "$case_repo/.agents/memory/DRAFT.md" \
    $'type: Agent Memory\ndescription: Invalid status\nstatus: []'
  expect_diagnostic "$case_repo" OKF005 .agents/memory/DRAFT.md 4 1
  assert_json_only_id OKF005
}

test_okf006_explicit_offset_timestamps() {
  local case_repo
  local entry
  local name
  local cases=(
    'generated|type: Agent Memory\ndescription: Invalid timestamp\ngenerated:\n  by: fixture\n  at: 2026-09-09T00:00:00'
    'verified|type: Agent Memory\ndescription: Invalid timestamp\nverified:\n  - by: fixture\n    at: 2026-09-09T00:00:00'
    'stale-after|type: Agent Memory\ndescription: Invalid timestamp\nstale_after: 2026-09-09'
    'source-last-modified|type: Agent Memory\ndescription: Invalid timestamp\nsources:\n  - resource: https://example.com\n    last_modified: 2026-09-09T00:00:00'
    'source-window-from|type: Agent Memory\ndescription: Invalid timestamp\nsources:\n  - resource: https://example.com\n    usage_window:\n      from: 2026-09-09T00:00:00\n      to: 2026-09-10T00:00:00Z'
    'source-window-to|type: Agent Memory\ndescription: Invalid timestamp\nsources:\n  - resource: https://example.com\n    usage_window:\n      from: 2026-09-09T00:00:00Z\n      to: 2026-09-10T00:00:00'
    'usage-window-from|type: Agent Memory\ndescription: Invalid timestamp\nusage_window:\n  from: 2026-09-09T00:00:00\n  to: 2026-09-10T00:00:00Z'
    'usage-window-to|type: Agent Memory\ndescription: Invalid timestamp\nusage_window:\n  from: 2026-09-09T00:00:00Z\n  to: 2026-09-10T00:00:00'
    'malformed-with-offset|type: Agent Memory\ndescription: Invalid timestamp\nstale_after: 2026-13-40T00:00:00+00:00'
  )

  for entry in "${cases[@]}"; do
    name="${entry%%|*}"
    case_repo="$(new_case_repo "okf006-$name")"
    write_concept "$case_repo/.agents/memory/DRAFT.md" "$(printf '%b' "${entry#*|}")"
    expect_diagnostic "$case_repo" OKF006 .agents/memory/DRAFT.md
  done
}

test_okf007_lowercase_reserved_paths() {
  local case_repo
  case_repo="$(new_case_repo okf007-index)"
  cp "$case_repo/.agents/memory/DRAFT.md" "$case_repo/.agents/memory/index.md"
  expect_diagnostic "$case_repo" OKF007 .agents/memory/index.md 1 1
  assert_json_only_id OKF007

  case_repo="$(new_case_repo okf007-nested-log)"
  cp "$case_repo/.agents/memory/DRAFT.md" "$case_repo/.agents/memory/testing/log.md"
  expect_diagnostic "$case_repo" OKF007 .agents/memory/testing/log.md 1 1
  assert_json_only_id OKF007

  case_repo="$(new_case_repo okf007-instruction-index)"
  cp "$case_repo/.agents/memory/DRAFT.md" "$case_repo/.agents/instructions/index.md"
  expect_diagnostic "$case_repo" OKF007 .agents/instructions/index.md 1 1
  assert_json_only_id OKF007

  case_repo="$(new_case_repo okf007-nested-instruction-log)"
  mkdir -p "$case_repo/.agents/instructions/nested"
  cp "$case_repo/.agents/memory/DRAFT.md" "$case_repo/.agents/instructions/nested/log.md"
  expect_diagnostic "$case_repo" OKF007 .agents/instructions/nested/log.md 1 1
  assert_json_only_id OKF007
}

test_okf101_every_path_derived_type() {
  local relative_path
  local case_repo
  local paths=(
    '.agents/instructions/repo.md'
    '.agents/memory/ARCHITECTURE.md'
    '.agents/memory/INDEX.md'
    '.agents/memory/LOG.md'
    '.agents/memory/KNOWN_ISSUES.md'
    '.agents/memory/known-issues/scripts.md'
    '.agents/memory/TESTING_STRATEGY.md'
    '.agents/memory/testing/scripts.md'
    '.agents/memory/adrs/hooks.md'
    '.agents/memory/sources/example-md.summary.md'
  )

  for relative_path in "${paths[@]}"; do
    case_repo="$(new_case_repo okf101-type)"
    sed -i.bak 's/^type: .*/type: Deliberately Wrong/' "$case_repo/$relative_path"
    rm -f "$case_repo/$relative_path.bak"
    expect_diagnostic "$case_repo" OKF101 "$relative_path" 2 1
  done
}

test_okf102_repository_escape() {
  local case_repo
  case_repo="$(new_case_repo okf102-link-escape)"
  cat >>"$case_repo/.agents/memory/DRAFT.md" <<'EOF'

[escape](../../../outside.md)
EOF
  expect_diagnostic "$case_repo" OKF102 .agents/memory/DRAFT.md 9 10

  case_repo="$(new_case_repo okf102-root-path)"
  write_concept "$case_repo/.agents/memory/DRAFT.md" $'type: Agent Memory\ndescription: Root-style resource\nresource: /README.md'
  expect_diagnostic "$case_repo" OKF102 .agents/memory/DRAFT.md 4 1

  case_repo="$(new_case_repo okf102-source-resource)"
  sed -i.bak 's#../../sources/example.md#../../../../outside.md#' \
    "$case_repo/.agents/memory/sources/example-md.summary.md"
  rm -f "$case_repo/.agents/memory/sources/example-md.summary.md.bak"
  expect_diagnostic "$case_repo" OKF102 .agents/memory/sources/example-md.summary.md

  case_repo="$(new_case_repo okf102-symlink-escape)"
  printf '%s\n' 'outside fixture repository' >"$TEST_ROOT/outside.md"
  ln -s "$TEST_ROOT/outside.md" "$case_repo/assets/outside-link.md"
  cat >>"$case_repo/.agents/memory/DRAFT.md" <<'EOF'

[symlink escape](../../assets/outside-link.md)
EOF
  expect_diagnostic "$case_repo" OKF102 .agents/memory/DRAFT.md
}

test_okf103_missing_local_targets() {
  local case_repo
  case_repo="$(new_case_repo okf103-link)"
  cat >>"$case_repo/.agents/memory/DRAFT.md" <<'EOF'

[missing](missing.md)
EOF
  expect_diagnostic "$case_repo" OKF103 .agents/memory/DRAFT.md 9 11

  case_repo="$(new_case_repo okf103-image)"
  cat >>"$case_repo/.agents/memory/DRAFT.md" <<'EOF'

![missing](missing.png)
EOF
  expect_diagnostic "$case_repo" OKF103 .agents/memory/DRAFT.md 9 12

  case_repo="$(new_case_repo okf103-resource)"
  write_concept "$case_repo/.agents/memory/DRAFT.md" $'type: Agent Memory\ndescription: Missing resource\nresource: missing.txt'
  expect_diagnostic "$case_repo" OKF103 .agents/memory/DRAFT.md 4 1

  case_repo="$(new_case_repo okf103-reference-definition)"
  cat >>"$case_repo/.agents/memory/DRAFT.md" <<'EOF'

[missing reference][target]

[target]: missing-reference.md
EOF
  expect_diagnostic "$case_repo" OKF103 .agents/memory/DRAFT.md

  case_repo="$(new_case_repo okf103-source-resource)"
  sed -i.bak 's#../../sources/example.md#../../sources/missing.md#' \
    "$case_repo/.agents/memory/sources/example-md.summary.md"
  rm -f "$case_repo/.agents/memory/sources/example-md.summary.md.bak"
  expect_diagnostic "$case_repo" OKF103 .agents/memory/sources/example-md.summary.md

  case_repo="$(new_case_repo okf103-directory)"
  write_concept "$case_repo/.agents/memory/DRAFT.md" \
    $'type: Agent Memory\ndescription: Directory resource\nresource: ../../assets'
  expect_diagnostic "$case_repo" OKF103 .agents/memory/DRAFT.md 4 1

  case_repo="$(new_case_repo okf103-missing-raw-source)"
  rm "$case_repo/.agents/sources/example.md"
  expect_diagnostic "$case_repo" OKF103 .agents/memory/sources/example-md.summary.md
  assert_json_only_id OKF103
}

test_markdown_destinations_and_masking() {
  local case_repo

  case_repo="$(new_case_repo markdown-balanced-destinations)"
  printf '%s\n' 'fixture' >"$case_repo/assets/balanced(name).md"
  printf '%s\n' 'fixture' >"$case_repo/assets/escaped).md"
  cat >>"$case_repo/.agents/memory/DRAFT.md" <<'EOF'
<!-- [ignored comment](missing-comment.md) -->
``[ignored inline](missing-inline.md)``
```markdown
[ignored fence](missing-fenced.md)
````
[nested [label]](../../assets/balanced(name).md)
[escaped destination](../../assets/escaped\).md)
[angle destination](<../../README.md>)
EOF
  run_linter "$case_repo" --format json
  assert_status 0
  assert_json_clean

  case_repo="$(new_case_repo markdown-location-after-mask)"
  cat >>"$case_repo/.agents/memory/DRAFT.md" <<'EOF'
<!-- [ignored comment](missing-comment.md) -->
``[ignored inline](missing-inline.md)``
```markdown
[ignored fence](missing-fenced.md)
````
[real destination](missing-real.md)
EOF
  expect_diagnostic "$case_repo" OKF103 .agents/memory/DRAFT.md 13 20
  assert_json_only_id OKF103

  case_repo="$(new_case_repo markdown-unclosed-fence)"
  cat >>"$case_repo/.agents/memory/DRAFT.md" <<'EOF'
```markdown
[masked through eof](missing-unclosed-fence.md)
EOF
  run_linter "$case_repo" --format json
  assert_status 0
  assert_json_clean

  case_repo="$(new_case_repo markdown-invalid-fence-opener)"
  cat >>"$case_repo/.agents/memory/DRAFT.md" <<'EOF'
```invalid`info
[real link](missing-invalid-fence.md)
```
EOF
  expect_diagnostic "$case_repo" OKF103 .agents/memory/DRAFT.md 9 13
  assert_json_only_id OKF103
}

test_nested_metadata_locations() {
  local case_repo

  case_repo="$(new_case_repo nested-source-location)"
  write_concept "$case_repo/.agents/memory/DRAFT.md" \
    $'type: Agent Memory\ndescription: Invalid nested resource\nsources:\n  - resource: ""'
  expect_diagnostic "$case_repo" OKF005 .agents/memory/DRAFT.md 5 5
  assert_json_only_id OKF005

  case_repo="$(new_case_repo nested-generated-location)"
  write_concept "$case_repo/.agents/memory/DRAFT.md" \
    $'type: Agent Memory\ndescription: Invalid generated metadata\ngenerated:\n  by: []\n  at: 2026-09-09T00:00:00Z'
  expect_diagnostic "$case_repo" OKF005 .agents/memory/DRAFT.md 5 3
  assert_json_only_id OKF005

  case_repo="$(new_case_repo nested-required-key-missing)"
  write_concept "$case_repo/.agents/memory/DRAFT.md" \
    $'type: Agent Memory\ndescription: Missing generated by\ngenerated:\n  at: 2026-09-09T00:00:00Z'
  expect_diagnostic "$case_repo" OKF005 .agents/memory/DRAFT.md 1 1
  assert_json_only_id OKF005
}

test_okf001_document_oserror() {
  local case_repo

  case_repo="$(new_case_repo okf001-document-oserror)"
  mkdir "$case_repo/.agents/memory/unreadable.md"
  expect_diagnostic "$case_repo" OKF001 .agents/memory/unreadable.md 1 1
  assert_json_only_id OKF001
}

test_okf104_manifest_binding() {
  local case_repo
  local manifest
  local summary

  case_repo="$(new_case_repo okf104-missing-entry)"
  manifest="$case_repo/.agents/memory/sources/source-ingest-manifest.json"
  python3 - "$manifest" <<'PY'
import json
import sys

path = sys.argv[1]
payload = json.load(open(path, encoding="utf-8"))
payload["entries"] = []
with open(path, "w", encoding="utf-8") as stream:
    json.dump(payload, stream, indent=2)
    stream.write("\n")
PY
  expect_diagnostic "$case_repo" OKF104 .agents/memory/sources/example-md.summary.md 1 1

  case_repo="$(new_case_repo okf104-duplicate-entry)"
  manifest="$case_repo/.agents/memory/sources/source-ingest-manifest.json"
  python3 - "$manifest" <<'PY'
import json
import sys

path = sys.argv[1]
payload = json.load(open(path, encoding="utf-8"))
payload["entries"].append(dict(payload["entries"][0]))
with open(path, "w", encoding="utf-8") as stream:
    json.dump(payload, stream, indent=2)
    stream.write("\n")
PY
  expect_diagnostic "$case_repo" OKF104 .agents/memory/sources/example-md.summary.md 1 1

  case_repo="$(new_case_repo okf104-wrong-source)"
  manifest="$case_repo/.agents/memory/sources/source-ingest-manifest.json"
  python3 - "$manifest" <<'PY'
import json
import sys

path = sys.argv[1]
payload = json.load(open(path, encoding="utf-8"))
payload["entries"][0]["source_path"] = "other.md"
with open(path, "w", encoding="utf-8") as stream:
    json.dump(payload, stream, indent=2)
    stream.write("\n")
PY
  expect_diagnostic "$case_repo" OKF104 .agents/memory/sources/example-md.summary.md 1 1

  case_repo="$(new_case_repo okf104-multiple-sources)"
  summary="$case_repo/.agents/memory/sources/example-md.summary.md"
  write_concept "$summary" $'type: Source Summary\ndescription: Too many bindings\nsources:\n  - resource: ../../sources/example.md\n  - resource: ../../sources/example.md'
  expect_diagnostic "$case_repo" OKF104 .agents/memory/sources/example-md.summary.md

  case_repo="$(new_case_repo okf104-draft-summary)"
  sed -i.bak 's#../../sources/pending.md#../../sources/example.md#' \
    "$case_repo/.agents/memory/sources/pending-md.summary.md"
  rm -f "$case_repo/.agents/memory/sources/pending-md.summary.md.bak"
  expect_diagnostic "$case_repo" OKF104 .agents/memory/sources/pending-md.summary.md
}

test_okf105_legacy_lifecycle() {
  local case_repo
  local value

  case_repo="$(new_case_repo okf105-coverage)"
  write_concept "$case_repo/.agents/memory/DRAFT.md" $'type: Agent Memory\ndescription: Legacy coverage\ncoverage: old description'
  expect_diagnostic "$case_repo" OKF105 .agents/memory/DRAFT.md 4 1

  for value in stable scaffold verified; do
    case_repo="$(new_case_repo "okf105-status-$value")"
    write_concept "$case_repo/.agents/memory/DRAFT.md" \
      "$(printf 'type: Agent Memory\ndescription: Legacy status\nstatus: %s' "$value")"
    expect_diagnostic "$case_repo" OKF105 .agents/memory/DRAFT.md 4 1
  done
}

test_stable_ordering_locations_and_human_json_parity() {
  local case_repo
  local first_output

  case_repo="$(new_case_repo stable-ordering)"
  sed -i.bak 's/^type: .*/type: Deliberately Wrong/' "$case_repo/.agents/instructions/repo.md"
  rm -f "$case_repo/.agents/instructions/repo.md.bak"
  sed -i.bak 's/^type: .*/type: Deliberately Wrong/' "$case_repo/.agents/memory/LOG.md"
  rm -f "$case_repo/.agents/memory/LOG.md.bak"
  run_linter "$case_repo" --format json
  assert_status 1
  assert_json_envelope
  assert_json_sorted
  first_output="$LAST_OUTPUT"

  run_linter "$case_repo" --format json
  assert_status 1
  [[ "$LAST_OUTPUT" == "$first_output" ]] || fail "JSON diagnostics are not deterministic"
  assert_human_json_parity "$case_repo"
}

test_okf900_untrusted_result() {
  local empty_repo="$TEST_ROOT/no-bundles"

  mkdir -p "$empty_repo"
  run_linter "$empty_repo" --format json
  assert_status 2
  assert_json_envelope
  assert_json_has OKF900 . 1 1
}

test_okf900_exit_precedence_with_ordinary_findings() {
  local case_repo
  local manifest

  case_repo="$(new_case_repo okf900-precedence)"
  manifest="$case_repo/.agents/memory/sources/source-ingest-manifest.json"
  printf '%s\n' '{not valid json' >"$manifest"
  sed -i.bak 's/^type: .*/type: Deliberately Wrong/' "$case_repo/.agents/memory/DRAFT.md"
  rm -f "$case_repo/.agents/memory/DRAFT.md.bak"

  run_linter "$case_repo" --format json
  assert_status 2
  assert_json_envelope
  assert_json_has_id OKF900
  assert_json_has_id OKF101
}

test_okf900_requires_vendored_pyyaml() {
  local case_repo
  local fake_global
  local isolated_linter
  local previous_pythonpath

  case_repo="$(new_case_repo okf900-missing-vendor)"
  fake_global="$TEST_ROOT/fake-global"
  isolated_linter="$TEST_ROOT/isolated-linter"
  mkdir -p "$fake_global/yaml"
  mkdir -p "$isolated_linter/vendor"
  cp "$LINTER_PATH" "$isolated_linter/lint-okf.py"
  chmod 755 "$isolated_linter/lint-okf.py"
  printf '%s\n' '__version__ = "6.0.3"' >"$fake_global/yaml/__init__.py"
  previous_pythonpath="${PYTHONPATH-}"
  export PYTHONPATH="$fake_global${PYTHONPATH:+:$PYTHONPATH}"
  run_linter_path "$case_repo" "$isolated_linter/lint-okf.py" --format json
  export PYTHONPATH="$previous_pythonpath"
  assert_status 2
  assert_json_envelope
  assert_json_has OKF900 . 1 1
}

cleanup() {
  if [[ -n "$TEST_ROOT" && -d "$TEST_ROOT" ]]; then
    rm -rf -- "$TEST_ROOT"
  fi
}

main() {
  validate_fixture_setup

  if [[ ! -x "$LINTER_PATH" ]]; then
    echo "intentional red: missing executable scripts/lint-okf.py" >&2
    exit 1
  fi

  assert_vendor_record
  TEST_ROOT="$(mktemp -d)"
  trap cleanup EXIT

  test_valid_corpus_and_public_output_contract
  test_okf001_non_utf8
  test_okf002_frontmatter_delimiters
  test_okf003_yaml
  test_okf004_required_fields
  test_okf005_standard_metadata_shapes
  test_okf005_non_scalar_status
  test_okf006_explicit_offset_timestamps
  test_okf007_lowercase_reserved_paths
  test_okf101_every_path_derived_type
  test_okf102_repository_escape
  test_okf103_missing_local_targets
  test_markdown_destinations_and_masking
  test_nested_metadata_locations
  test_okf001_document_oserror
  test_okf104_manifest_binding
  test_okf105_legacy_lifecycle
  test_stable_ordering_locations_and_human_json_parity
  test_okf900_untrusted_result
  test_okf900_exit_precedence_with_ordinary_findings
  test_okf900_requires_vendored_pyyaml

  echo "PASSED: OKF linter CLI contract"
}

main "$@"
