# T15b Node archive extraction boundary

This is a decision for the future installer, not implemented installation behavior. T15b-controller remains admission-only. Existing unowned, linked or customized destination collisions still refuse.

## Observed pinned archive

The selected macOS arm64 archive is Node v24.22.1, SHA256 `654ba79de6155647e22321932b45f2a1ccb705976cc337c9b8e278beb085a628`, matching the existing release contract and [official release checksums](https://nodejs.org/download/release/v24.22.1/SHASUMS256.txt). The retained file is `/private/tmp/factory-node-v24.22.1-darwin-arm64-selection.tar.xz`. Inspecting all 5,888 members finds regular files, directories and exactly three symbolic links, with no hard links or special entries:

| Path below `node-v24.22.1-darwin-arm64/` | Link target |
| --- | --- |
| `bin/corepack` | `../lib/node_modules/corepack/dist/corepack.js` |
| `bin/npx` | `../lib/node_modules/npm/bin/npx-cli.js` |
| `bin/npm` | `../lib/node_modules/npm/bin/npm-cli.js` |

A blanket refusal of every member link would reject the already-selected official archive. The installer will deliberately omit only these exact convenience entries, after validating their exact names and targets against a platform-specific extraction policy. It will not follow or recreate them. Extract the verified regular payload and directories into a newly created private owned stage; reject every unexpected link, device, duplicate/case-colliding path, traversal, absolute path or unsupported entry before extraction. Bound archive size, member count and expanded bytes. Bind the installed inventory to the selected archive digest and the exact omission policy. Validate the entire resulting tree before publication. A changed archive, even with matching-looking member names, cannot substitute for the pinned selection.

Run npm through the staged regular executable and regular script: `node/bin/node node/lib/node_modules/npm/bin/npm-cli.js` on the observed POSIX layout, using absolute validated paths. Do not depend on `bin/npm`, shell resolution, Corepack or npx. Verify other selected platforms' actual member layouts before admitting a platform-specific policy. Linux and Windows archive extraction are not proven by the macOS observation.

## Toolchain executable links

Install the dedicated approved toolchain with `npm ci --ignore-scripts --no-bin-links`, explicit cache and controlled npm configuration. This avoids generated executable links or Windows command shims. The runtime already invokes the compiler's regular `node_modules/typescript/bin/tsc` directly through Node (`src/build.ts`), so it does not need `.bin` links. The pinned npm 11.19.1 documentation bundled in the verified Node archive, `lib/node_modules/npm/docs/content/using-npm/config.md`, documents `bin-links`; the [npm v11 configuration documentation](https://docs.npmjs.com/cli/v11/using-npm/config/#bin-links) also describes the option. Future dependency maintenance must preserve this policy and validate the actual installed closure. Unexpected links remain a refusal rather than an ownership shortcut.

## Disposable evidence and limits

On 2026-10-22, a new disposable directory received only regular files and directories from the exact verified archive, after checking the complete expected link table. The extracted tree contained no symlinks. Its direct Node executable returned `v24.22.1`; its direct npm script returned `11.19.1`, both exit 0. Receipt: `/tmp/factory-node-archive-omission-proof.json`; extraction: `/tmp/factory-node-link-omission-mnme5ooj/`.

A separate disposable toolchain received only the approved declaration and lock. Pinned Node/npm ran offline `ci --ignore-scripts --no-bin-links --audit=false --fund=false` with temporary HOME and absent user/global npm configuration. Installation exited 0, package and lock hashes stayed unchanged, and the entire resulting tree contained no symlinks. Direct compiler execution returned `Version 7.0.2`, exit 0. Receipt: `/tmp/factory-node-install-link-policy-proof.json`; npm log: `/tmp/factory-no-bin-links-2mjlqo1_/npm-result.log`.

These checks establish the macOS extraction and direct-command feasibility of the chosen policy. They do not test a production installer, malicious archive handling, publication, Windows image lifetime, installed ownership, or native Linux/Windows extraction. T15b-install must add its public positive, hostile-entry, interruption and ownership proofs; T17 must retain platform qualification.
