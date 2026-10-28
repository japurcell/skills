#!/usr/bin/env bash

set -Eeuo pipefail

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd -P)"
readonly SCRIPT_DIR
readonly REPO_ROOT="$(cd -- "$SCRIPT_DIR/.." && pwd -P)"

usage() {
  cat <<'EOF'
Usage:
  copy-from-git.sh [--clone-dir NAME] --repo URL [--] SRC DEST [SRC DEST ...]
  copy-from-git.sh [--clone-dir NAME] URL SRC DEST [SRC DEST ...]

Options:
  -r, --repo URL        Repository URL (or local Git repository path).
  -c, --clone-dir NAME  Clone folder name under the repository's parent directory.
                       Defaults to the repository basename without .git.
  -h, --help            Show this help and exit.
  --                   End options; remaining arguments are source/destination pairs.

Example:
  copy-from-git.sh --repo https://github.com/example/skills.git \
    --clone-dir example-skills -- docs vendor/docs

Existing clones must match the requested remote. Collisions fail with an error;
choose another --clone-dir. Matching clones run git pull --ff-only, with fetch
and reset --hard to the remote default branch as recovery if pulling fails.
Directory sources copy recursively; use path/to/dir/. to copy their contents.
Destinations are relative to this repository and cannot contain '..'.
Exit codes: 0 success/help, 1 repository/dependency error, 2 usage/copy error.
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
  if [[ -d "$url" ]]; then
    (cd -- "$url" && pwd -P)
    return
  fi
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
  local clone_name="$2"
  local parent_dir="${REPO_ROOT}/.."
  local repo_dir="${parent_dir%/}/$clone_name"

  if [[ -e "$repo_dir" || -L "$repo_dir" ]]; then
    if ! same_remote "$repo_dir" "$repo_url"; then
      err "Clone path already exists and does not match $repo_url: $repo_dir"
      err "Choose a different folder with --clone-dir NAME."
      return 1
    fi
    if ! update_existing_repo "$repo_dir"; then
      err "Could not update $repo_url at $repo_dir; see Git diagnostics above."
      return 1
    fi
  else
    log "Cloning $repo_url into $repo_dir"
    if ! git clone -- "$repo_url" "$repo_dir" >&2; then
      err "Could not clone $repo_url into $repo_dir; check the URL, access, and Git diagnostics above."
      return 1
    fi
  fi
  printf '%s\n' "$repo_dir"
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
    err "Source path does not exist: $src"
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
  local repo_url="" clone_name=""
  local -a paths=()
  while (( $# )); do
    case "$1" in
      -h|--help) usage; return 0 ;;
      -r|--repo|-c|--clone-dir)
        if (( $# < 2 )) || [[ -z "$2" || "$2" == -* ]]; then
          err "Option $1 requires a value. See --help."
          return 2
        fi
        case "$1" in
          -r|--repo) repo_url="$2" ;;
          *) clone_name="$2" ;;
        esac
        shift 2 ;;
      --repo=|--clone-dir=) err "Option ${1%%=*} requires a value. See --help."; return 2 ;;
      --repo=*) repo_url="${1#*=}"; shift ;;
      --clone-dir=*) clone_name="${1#*=}"; shift ;;
      --) shift; paths+=("$@"); break ;;
      -*) err "Unknown option: $1. See --help."; return 2 ;;
      *)
        if [[ -z "$repo_url" ]]; then repo_url="$1"
        else paths+=("$1"); fi
        shift ;;
    esac
  done
  if [[ -z "$repo_url" ]] || (( ${#paths[@]} < 2 || ${#paths[@]} % 2 != 0 )); then
    err "Provide a repository and source/destination pairs. See --help."
    return 2
  fi
  [[ -n "$clone_name" ]] || clone_name="$(repo_name_from_url "$repo_url")"
  case "$clone_name" in
    .|..|*/*|*\\*|-*) err "Clone folder must be a single folder name: $clone_name"; return 2 ;;
  esac
  local i
  for (( i=1; i<${#paths[@]}; i+=2 )); do
    resolve_dest "${paths[i]}" >/dev/null || return 2
  done

  require_cmd git
  require_cmd basename
  require_cmd dirname
  require_cmd mkdir
  require_cmd cp

  # Git stores local clone origins as absolute paths. Use the same physical path
  # for cloning and comparison so relative paths and symlinks can be reused.
  if [[ -d "$repo_url" ]]; then
    repo_url="$(cd -- "$repo_url" && pwd -P)" || return 1
  fi

  local repo_root
  if ! repo_root="$(prepare_repo "$repo_url" "$clone_name")"; then
    return 1
  fi
  set -- "${paths[@]}"
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
    if [[ ! -e "$full_src" ]]; then
      err "Missing source path '$rel_src' in repository $repo_url. It may have moved or been removed upstream. Update or remove this source mapping in scripts/import-skill-repos.sh."
      failures=$((failures + 1))
      continue
    fi
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
