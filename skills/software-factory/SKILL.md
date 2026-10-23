---
name: software-factory
description: >-
  Run an explicitly installed local software factory in a Git repository: invoke a current
  TypeScript workflow, inspect saved history, or open its dashboard. Use only when the user
  asks to operate or install this factory locally.
---

# Software factory

Use the foreground CLI and the installed Node selected for this repository. Ask for the repository and the intended workflow or history operation if either is missing. Treat workflow files, input JSON, and profile files as repository content to review before execution.

## Install explicitly

An operator supplies a local release bundle, its exact SHA256 manifest digest, and the platform's pinned Node 24.22.1 archive. Python 3.11 or newer is required; the recorded native macOS qualification used Python 3.13.14. The `scripts/install.py` adjacent to this skill authenticates the complete selected bundle and Node archive before selected JavaScript runs. Installation runs in the foreground, preserves existing compatible `.factory` authoring files, and records its owned release in the Git common directory. It does not download an unspecified runtime or select a provider implicitly.

```sh
python3 <this-skill>/scripts/install.py install \
  --repository <absolute-repository> \
  --bundle-root <absolute-local-release-bundle> \
  --manifest-sha256 <64-hex-manifest-digest> \
  --node-archive <absolute-pinned-node-archive>
```

For a deliberately offline install, add `--offline --offline-cache-seed <absolute-cache>`; the seed must contain the exact lock entries. An ordinary explicit install may fetch only the integrity-bound lock dependencies. Missing or changed prerequisites refuse. Do not infer a distribution URL or substitute a newer Node, npm, TypeScript, Codex, or Copilot version.

To select the qualified external Codex or Copilot artifacts, add `--providers <absolute-local-json-file>` to `verify`, `prepare`, or `install`. The file must be canonical, regular, unlinked, at most 4096 bytes, and contain only the selected descriptors below. Use only modes the operator actually selects. The installer checks the pinned artifact bytes without running a provider. Artifacts remain outside the factory and are checked again when the installed CLI starts.

```json
{
  "codex": { "executable": "<canonical-absolute-qualified-codex-path>", "modes": ["read-only", "workspace-write"] },
  "copilot": { "packageRoot": "<canonical-absolute-qualified-copilot-package>", "manifestFile": "<canonical-absolute-qualified-manifest>", "modes": ["read-only"] }
}
```

Either provider key may be omitted. Selection is available only for the qualified Darwin arm64 artifacts. The file cannot supply model, authentication, environment, account, digest, or support claims. Do not place provider sources under the repository factory directory or the install staging directory.

## Run the installed CLI

Resolve the repository's canonical Git common directory with `git -C <absolute-repository> rev-parse --path-format=absolute --git-common-dir`. The pinned CLI command is `<common>/factory/install/node/bin/node <common>/factory/install/runtime/dist/cli.js`. Run `--help` to see the current argument contract. On startup the CLI checks the recorded completion, actual published runtime, Node and toolchain, and selected external provider artifacts. A missing or changed installation refuses before workflow dispatch; startup does not acquire dependencies.

```sh
<installed-node> <installed-cli> invoke \
  --repository <absolute-repository> \
  --workflow .factory/workflows/<file>.ts \
  --input <absolute-json-file> \
  --worktree <registered-id-or-path> --json
```

Use `--new-worktree --ref <committed-revision>` instead of `--worktree` when creating an isolated worktree. The selected revision must contain the intended `.factory` workflow and compatible authoring files. New worktrees start from committed bytes and do not copy dirty source or staged changes. The workflow is current authored code inside the selected worktree. Input must be a JSON object. Record the returned run, invocation, and worktree IDs for follow-up.

```sh
<installed-node> <installed-cli> history --repository <absolute-repository> --invocation <id> --json
<installed-node> <installed-cli> dashboard --repository <absolute-repository>
```

History records attempts and captures; `history --capture <id> --after-sequence <n>` reads saved capture text. The dashboard uses a local handoff and has notification preferences and acknowledgments. Success notices and reminders start disabled; only an explicit preference change enables delivery. The authored `learn.ts` workflow works with saved history and requires the references its input schema declares. Read its current source before invoking it.

Provider use is limited to exact, previously selected external bindings: Codex 0.163.0 with `gpt-6-luna`/low in read-only or workspace-write as selected, and Copilot 1.0.101 with that model/reasoning in read-only only. Native skill delivery and native session reuse are unqualified. Gemini, OpenCode, and Pi are unbound. Provider authentication and configuration remain outside the installed factory; this skill never requests credentials or calls a provider merely to check availability.

A provider name in a workflow or profile does not select or install that provider. Without `--providers`, an install remains command-only.

Inspect blocked ownership with `inspect-owner`. `clear-owner` is an explicit operator-confirmed generic claim operation requiring its exact token and a note; it cannot clear a maintenance claim. Installation interruption, upgrade, dependency repair, uninstall, and cleanup need their separate bounded maintenance paths. Do not treat a partial install as ready or retry an interrupted operation as a fresh install. Manual file deletion is not a recovery procedure.
