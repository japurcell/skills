# Retiring an older scan-secrets installation

This repository no longer installs or maintains the standalone scanner or its
repository Git gates. A normal provider upgrade removes exactly owned retired
provider registrations and unchanged hook assets. It does not search for
standalone scanner bundles or discover and uninstall repository-local Git gates.
Those require a one-time, operator-managed retirement.

## Uninstall active repository gates first

An activated gate uses the standalone scanner bundle. Uninstall every active gate
before removing that bundle. Gate installation and uninstallation were supported
only on POSIX; the legacy command rejects other platforms as unverified. The
legacy standalone CLI bundle itself had platform-specific locations:

- POSIX executable bundle: `~/.local/lib/scan-secrets`
- Windows executable bundle: `%LOCALAPPDATA%\Programs\scan-secrets`
- POSIX data: `$XDG_DATA_HOME/scan-secrets`, or `~/.local/share/scan-secrets` on
  Linux and `~/Library/Application Support/scan-secrets` on macOS when
  `XDG_DATA_HOME` is unset
- Windows data: `%LOCALAPPDATA%\scan-secrets`

The data directory is separate from the executable bundle. Preserve scanner
reports, audit history, and other data unless you have separately decided to
archive or remove it.

Use the installed legacy `scan-secrets` executable and an explicit repository
path. On POSIX, preview with the exact scope and Git executable used for the
installation:

```sh
/absolute/path/to/scan-secrets/scan-secrets hooks uninstall \
  --repo /absolute/path/to/repository \
  --git /absolute/path/to/git \
  --scope repository \
  --dry-run --json
```

If the gate was installed with worktree scope, use `--scope worktree` instead.
On macOS, choose a direct Git binary; `/usr/bin/git` may be an Apple launcher
that the legacy preview refuses. Review the JSON preview and proceed only when
the ownership and proposed restoration match the intended repository. The
preview exits 0 with `outcome: "preview"` and makes no changes. Run the same
command without `--dry-run` to uninstall. A successful change exits 0 with
`outcome: "uninstalled"`; an already absent installation is a successful no-op.
The legacy CLI documents exit 2 for unavailable infrastructure or lock
contention, 3 for invalid or unsupported configuration, and 130 for cancellation.

The ownership-checked uninstall restores the exact prior `core.hooksPath` binding
and preserves original hooks and unrelated settings. It may retain private
recovery metadata and backups under the repository's `.git/scan-secrets`
directory. Preserve those records for review; do not delete that directory by
guess. If the preview reports drift, invalid ownership, or an unsupported scope,
stop and preserve the repository configuration and all private recovery files.

If the installed launcher is already missing, use the source from the pinned
pre-removal revision `5db7440017e081b4d391c92f28d325b2fccf95a0`, after confirming
that this revision is available from a trusted local checkout. The old source
entrypoint can run the same ownership-checked command:

```sh
python3 -I -S -B /path/to/pre-removal-checkout/scripts/scan-secrets.py \
  hooks uninstall --repo /absolute/path/to/repository \
  --git /absolute/path/to/git --scope repository --dry-run --json
```

Review the preview, then repeat without `--dry-run`. Do not use source from an
unverified revision or continue if its ownership checks fail.

## Review and remove the standalone bundle

Only after all active repository gates have been uninstalled, inspect the
standalone bundle's root `installation.json`. It records the exact files and
SHA-256 hashes owned by that legacy installation. Compare every listed file
against its recorded hash, and inspect the entire bundle for modified, missing,
or unlisted entries before cleanup. If ownership is ambiguous or any content has
changed, preserve the bundle and request manual review. Otherwise remove only
the verified manifest-listed files using an appropriate per-file file manager or
administrative tool, then remove empty directories. Do not use a wildcard or
recursive directory deletion. Keep scanner data, logs, unrelated files, and
repository recovery records unless they have been separately reviewed.

Neither the current provider installers nor the legacy standalone installer
perform this bundle or repository discovery automatically.
