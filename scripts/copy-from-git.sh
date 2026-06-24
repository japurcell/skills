#!/usr/bin/env bash

set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
readonly SCRIPT_DIR
readonly REPO_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd -P)"

usage() {
  cat <<'EOF'
Usage:
  ./import-skill-repos.sh <github_repo_url> <src1> <dest1> [<src2> <dest2> ...]

Example:
  ./import-skill-repos.sh \
    https://github.com/example/repo.git \
    README.md third_party/README.md \
    docs vendor/docs

Notes:
  - If ../<repo-name> already exists and is the same repo, the script always runs:
      git pull --ff-only
    before copying.
  - If that fails, it attempts:
      git fetch origin --prune
      git reset --hard origin/<default-branch>
  - If src is a directory, it copies the directory recursively.
  - If you want directory contents copied into a destination, pass src as:
      path/to/dir/.
EOF
}

log()  { printf '[INFO] %s\n' "$*" >&2; }
warn() { printf '[WARN] %s\n' "$*" >&2; }
err()  { printf '[ERROR] %s\n' "$*" >&2; }

cleanup() {
  local code=$?
  if [[ $code -ne 0 ]]; then
    err "Script failed with exit code $code"
  fi
}
trap cleanup EXIT

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || {
    err "Required command not found: $1"
    exit 1
  }
}

repo_name_from_url() {
  local url="$1"
  local name
  name="$(basename "$url")"
  name="${name%.git}"
  [[ -n "$name" && "$name" != "." && "$name" != "/" ]] || {
    err "Could not determine repo name from URL: $url"
    exit 1
  }
  printf '%s\n' "$name"
}

normalize_remote() {
  local url="$1"
  url="${url%.git}"
  url="${url#git@github.com:}"
  url="${url#https://github.com/}"
  url="${url#http://github.com/}"
  printf '%s\n' "$url"
}

same_remote() {
  local repo_dir="$1"
  local expected_url="$2"

  [[ -d "$repo_dir/.git" ]] || return 1

  local actual_url
  actual_url="$(git -C "$repo_dir" remote get-url origin 2>/dev/null || true)"
  [[ -n "$actual_url" ]] || return 1

  [[ "$(normalize_remote "$actual_url")" == "$(normalize_remote "$expected_url")" ]]
}

default_branch_for_remote() {
  local repo_dir="$1"
  local ref

  ref="$(git -C "$repo_dir" symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null || true)"
  if [[ -n "$ref" ]]; then
    printf '%s\n' "${ref#origin/}"
    return 0
  fi

  ref="$(git -C "$repo_dir" remote show origin 2>/dev/null | sed -n 's/.*HEAD branch: //p' | head -n1 || true)"
  if [[ -n "$ref" ]]; then
    printf '%s\n' "$ref"
    return 0
  fi

  # Common fallback guesses
  if git -C "$repo_dir" show-ref --verify --quiet refs/remotes/origin/main; then
    printf 'main\n'
    return 0
  fi
  if git -C "$repo_dir" show-ref --verify --quiet refs/remotes/origin/master; then
    printf 'master\n'
    return 0
  fi

  return 1
}

update_existing_repo() {
  local repo_dir="$1"
  log "Found existing matching repo: $repo_dir"
  log "Pulling latest changes with git pull --ff-only"

  if git -C "$repo_dir" pull --ff-only >&2; then
    log "git pull succeeded"
    return 0
  fi

  warn "git pull failed; attempting recovery with fetch + hard reset"

  local branch
  if ! git -C "$repo_dir" fetch origin --prune >&2; then
    warn "git fetch failed"
    return 1
  fi

  if ! branch="$(default_branch_for_remote "$repo_dir")"; then
    warn "Could not determine remote default branch"
    return 1
  fi

  log "Resetting local repo to origin/$branch"
  if git -C "$repo_dir" reset --hard "origin/$branch" >&2; then
    log "Repository reset to origin/$branch"
    return 0
  fi

  warn "git reset --hard origin/$branch failed"
  return 1
}

prepare_repo() {
  local repo_url="$1"
  local parent_dir="${REPO_ROOT}/.."
  local repo_name preferred_dir temp_dir repo_dir

  mkdir -p "$parent_dir"
  repo_name="$(repo_name_from_url "$repo_url")"
  preferred_dir="${parent_dir%/}/$repo_name"

  for repo_dir in "$parent_dir"/*; do
    [[ -d "$repo_dir" ]] || continue
    [[ "$repo_dir" == *.clone.* ]] && continue

    if ! same_remote "$repo_dir" "$repo_url"; then
      continue
    fi

    if update_existing_repo "$repo_dir"; then
      printf '%s\n' "$repo_dir"
      return 0
    fi
    warn "Could not safely update existing repo; falling back to fresh temp clone"
    break
  done

  if [[ ! -e "$preferred_dir" ]]; then
    log "Cloning into preferred location: $preferred_dir"
    if git clone "$repo_url" "$preferred_dir" >&2; then
      printf '%s\n' "$preferred_dir"
      return 0
    fi
    warn "Clone into preferred location failed"
  else
    warn "Preferred path exists but is not a matching usable git repo: $preferred_dir"
  fi

  temp_dir="$(mktemp -d "${parent_dir%/}/${repo_name}.clone.XXXXXX")"
  log "Cloning into fallback temp dir: $temp_dir"
  git clone "$repo_url" "$temp_dir" >&2
  printf '%s\n' "$temp_dir"
}

copy_with_rsync() {
  local src="$1"
  local dest="$2"
  mkdir -p "$(dirname "$dest")"
  rsync -a -- "$src" "$dest"
}

copy_with_cp() {
  local src="$1"
  local dest="$2"
  mkdir -p "$(dirname "$dest")"
  cp -R -- "$src" "$dest"
}

copy_path() {
  local src="$1"
  local dest="$2"

  if [[ ! -e "$src" ]]; then
    warn "Source not found, skipping: $src"
    return 1
  fi

  if command -v rsync >/dev/null 2>&1; then
    if copy_with_rsync "$src" "$dest"; then
      log "Copied with rsync: $src -> $dest"
      return 0
    fi
    warn "rsync failed, falling back to cp: $src -> $dest"
  fi

  if copy_with_cp "$src" "$dest"; then
    log "Copied with cp: $src -> $dest"
    return 0
  fi

  err "Copy failed: $src -> $dest"
  return 1
}

resolve_dest() {
  local rel_dest="$1"
  local cleaned="${rel_dest#./}"

  if [[ "$rel_dest" = /* ]]; then
    err "Absolute destination paths are not allowed: $rel_dest"
    return 1
  fi

  [[ -n "$cleaned" && "$cleaned" != "." ]] || {
    err "Destination must not be empty or '.'"
    return 1
  }

  case "/$cleaned/" in
    */../*|*/..)
      err "Destination must not contain '..': $rel_dest"
      return 1
      ;;
  esac

  printf '%s\n' "${REPO_ROOT}/${cleaned}"
}

main() {
  require_cmd git
  require_cmd basename
  require_cmd dirname
  require_cmd mkdir
  require_cmd cp

  if [[ $# -lt 3 ]]; then
    usage
    exit 1
  fi

  local repo_url="$1"
  shift

  if (( $# % 2 != 0 )); then
    err "Source/destination arguments must be provided in pairs"
    usage
    exit 1
  fi

  local repo_root
  repo_root="$(prepare_repo "$repo_url")"
  log "Using repo root: $repo_root"

  local failures=0
  local rel_src rel_dest full_src full_dest

  while [[ $# -gt 0 ]]; do
    rel_src="$1"
    rel_dest="$2"
    shift 2

    full_src="${repo_root}/${rel_src}"

    if ! full_dest="$(resolve_dest "$rel_dest")"; then
      failures=$((failures + 1))
      continue
    fi

    log "Processing: $rel_src -> $rel_dest"
    if ! copy_path "$full_src" "$full_dest"; then
      failures=$((failures + 1))
    fi
  done

  if (( failures > 0 )); then
    err "$failures copy operation(s) failed"
    exit 2
  fi

  log "All operations completed successfully"
}

main "$@"