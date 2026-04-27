#!/usr/bin/env bash

set -euo pipefail

readonly REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
readonly SKILLS_ROOT="${CLEANUP_SKILLS_ROOT:-$REPO_ROOT/skills}"

dir_creation_epoch() {
  local dir="$1"
  local created

  if created="$(stat -c %W "$dir" 2>/dev/null)"; then
    if [[ "$created" -gt 0 ]]; then
      printf '%s\n' "$created"
      return
    fi
    stat -c %Y "$dir"
    return
  fi

  created="$(stat -f %B "$dir")"
  if [[ "$created" -gt 0 ]]; then
    printf '%s\n' "$created"
    return
  fi
  stat -f %m "$dir"
}

workspace_report() {
  local workspace="$1"
  local kept="$2"
  local deleted="$3"

  printf 'workspace=%s kept=%s deleted=%s\n' \
    "$(basename "$workspace")" \
    "$kept" \
    "$deleted"
}

prune_workspace_iterations() {
  local workspace="$1"
  local -a iterations=()
  local -a ordered=()
  local iteration
  local kept_path
  local kept_name
  local deleted_names=""

  while IFS= read -r -d '' iteration; do
    iterations+=("$iteration")
  done < <(find "$workspace" -mindepth 1 -maxdepth 1 -type d -name 'iteration-*' -print0)

  if [[ "${#iterations[@]}" -eq 0 ]]; then
    workspace_report "$workspace" "none" "nothing-to-prune"
    return
  fi

  if [[ "${#iterations[@]}" -eq 1 ]]; then
    workspace_report "$workspace" "$(basename "${iterations[0]}")" "nothing-to-prune"
    return
  fi

  while IFS= read -r ordered_entry; do
    ordered+=("${ordered_entry#*	}")
  done < <(
    for iteration in "${iterations[@]}"; do
      printf '%s\t%s\n' "$(dir_creation_epoch "$iteration")" "$iteration"
    done | sort -n
  )

  kept_path="${ordered[${#ordered[@]}-1]}"
  kept_name="$(basename "$kept_path")"

  for iteration in "${ordered[@]:0:${#ordered[@]}-1}"; do
    rm -rf "$iteration"
    if [[ -n "$deleted_names" ]]; then
      deleted_names+=","
    fi
    deleted_names+="$(basename "$iteration")"
  done

  workspace_report "$workspace" "$kept_name" "$deleted_names"
}

main() {
  local workspace

  [[ -d "$SKILLS_ROOT" ]] || {
    echo "Skills root not found: $SKILLS_ROOT" >&2
    exit 1
  }

  while IFS= read -r -d '' workspace; do
    prune_workspace_iterations "$workspace"
  done < <(find "$SKILLS_ROOT" -mindepth 1 -maxdepth 1 -type d -name '*-workspace' -print0 | sort -z)
}

main "$@"
