---
type: Research Findings
description: Verified distribution lessons from skills-lock, Superpowers, wshobson/agents, and Skillet
---

# Distribution Reference Findings

Research date: 2026-09-29. Sources are each project's first-party GitHub repository pages, README, manifest, changelog, and release page. The snapshot versions and commits below are evidence for this review, not recommended pins for this repository.

## Decision

**No example justifies changing the approved initial delivery contract.** Keep committed selected runtime copies, pinned source revision and digest, one maintained source/catalog with declared dependencies, Python stdlib lifecycle and client adapters, preflight conflict detection, tracked ownership and conservative pruning, and restoration from the currently recorded revision. The examples provide implementation acceptance details and future-channel evidence, especially frozen verification and native output generation, but no missing product capability that calls for replacing committed copies or broadening initial transport.

The most useful additional implementation checks are:

- A restore/preflight mode should prove the selected manifest, resolved immutable revision, and content digests match without resolving a moving ref or writing files. `skills-lock`'s `--frozen` behavior is a good model for integrity and CI semantics. Since this project commits the delivered files, the installer should verify the committed payload against its metadata. This reinforces the approved SHA-256 and immutable-commit requirement; it does not require a second remote lockfile mechanism.
- Each adapter should explicitly declare the client-native files it emits and what the client actually consumes. A plugin installer may discard unrecognized files, and a context/bootstrap file must be declared in a recognized manifest field. Validate generated output against the component contract, rather than assuming a common plugin manifest transports every source file.
- For user-local developer convenience, symlinks can be explored later as an opt-in mode with a tested copy fallback. They are not appropriate as the committed team default: a link can target outside the clone, be broken by clone movement, and needs platform-specific creation and permission behavior. `skillet` itself documents symlink-first operation and copy fallback in its v1.1.0 release notes, but the approved committed-copy mode avoids making that portability choice a prerequisite.
- Treat vendored skill dependencies, which appear inside distribution bundles, as an explicit source and licensing/provenance question. Do not turn arbitrary external Git, archive, or OCI resolution into initial installer scope. Skillet shows those transports are feasible for skills, while also explicitly excluding agents, hooks, plugins, and LSP configuration from its skills-only manifest profile.

No change is recommended to the already-set decisions on clients, bundle and individual selection, local untracked mode, explicit update command, preservation of local edits, no automatic merge, no rollback, ownership-aware pruning, global/project coexistence, or supported operating systems. Native package publishing stays a later channel. These four examples do not establish broad client compatibility or validate this repository's eventual adapters.

## Reference comparison

| Project and observed snapshot | What it demonstrates | Boundary or maturity caveat | Contract effect |
| --- | --- | --- | --- |
| [luisalima/skills-lock](https://github.com/luisalima/skills-lock), README on `main`; MIT; six commits visible; no release shown | Manifest plus lock records full Git commit, selected path, and SHA-256 tree integrity. `install --frozen` performs no ref resolution or lock writes and errors on drift. Its threat model covers hostile manifests, Git option injection, path escapes, and symlink rejection. | README calls it a working prototype, excludes skill dependencies and global scope, and its repository page shows no release. Node 18+ and Git required. | Strengthens hash verification and frozen semantics in implementation acceptance. Does not supersede the committed-copy contract. |
| [obra/superpowers](https://github.com/obra/superpowers), `.claude-plugin/plugin.json` version 6.4.2, MIT; visible `main` history includes `b36e082` (2026-08-12) | One maintained skill source is delivered through distinct harness channels. Its porting guide describes external marketplace sync for Codex, Git-URL extension install for Gemini/OpenCode, and declared bootstrap context for a harness that strips undeclared files. | README says install/update varies by harness and often updates automatically. Marketplace/plugin surfaces have distinct trust, approval, and update behavior. The guide is an adapter-maintenance workload example, not proof that one package handles every asset uniformly. | Supports a maintained catalog plus per-client adapters and manifests. Confirms native distribution can be additive later. |
| [wshobson/agents](https://github.com/wshobson/agents), MIT; visible `main` head activity includes `a30778f` (2026-09-01); no product version claimed in the root README | `plugins/` is described as one source-of-truth with harness-native generation. Granular plugins group agents, commands, and skills; separate skills-only install paths intentionally omit agents and commands. Some generated trees are committed, others ignored and generated locally. | Documentation counts and harness matrix describe this repository's current state; they are not transferable compatibility guarantees. It documents clone/generate/symlink for some clients and marketplace registries for others, so even one catalog requires channel-specific setup. | Validates curated bundles plus individual skills as distinct selectors. Supports future generated native outputs from maintained sources, without requiring generators as the first delivery route. |
| [echohello-dev/skillet](https://github.com/echohello-dev/skillet), v1.1.0 release at commit `ac839a9` (2026-06-20), Apache-2.0 | A packaged, multi-OS skills CLI can resolve Git sources, safe HTTP archives, local directories, and OCI digests; its lock output is deterministic. Release notes list Git, archive, and OCI resolvers, symlink install with copy fallback, and check/update flows. | Its README calls check/update “in progress” while also listing those commands in v1.1.0 and saying stable commands exclude them / flag them. Therefore do not treat its update guarantees as established. The manifest explicitly ignores plugins, hooks, marketplaces, and MCP/LSP dependencies. | Good evidence for later optional transport/package exploration, not a reason to adopt OCI or a runtime dependency for this full repository installer. Its skill-only profile is a mismatch for the initial complete bundle. |

## Detail by requirement

### Frozen restoration and integrity

`skills-lock` separates dependency declaration from resolution: an ordinary install resolves a source, while frozen install verifies the lock and hashes without resolution or lockfile writes. Its hash covers a skill file tree, not only a Git ref, and it refuses symlinks. This adds a useful distinction to the implementation plan: immutable commit provenance answers which upstream revision was selected; a digest check answers whether the committed/restored bytes still match. Keep both checks. The already-approved contract restores the *currently recorded revision* and explicitly excludes retained-history rollback; none of these examples changes that boundary.

Skillet also documents lockfile generation and digest-pinned OCI sources, but its own README's conflicting maturity labels do not support relying on its update command as proven behavior. The user-approved installer's update behavior must be validated against this repository's accepted lifecycle contract.

### Canonical sources and generated adapters

Superpowers and wshobson/agents show that “one source” does not mean “one output format.” The wshobson repository documents harness-native output differences, including translating commands to skill/prompt forms and using different install paths; the Superpowers porting guide warns that installers can strip undeclared files and makes bootstrap delivery contingent on a recognized manifest field. This aligns with the existing decision to retain provider-specific adapters and generate only supported components for later native packages. Avoid introducing additional client surfaces until their components can be verified against real clients, as required by the closed contract.

### Selection granularity

The examples separate three units that should not be conflated: an individually installable skill; a plugin/bundle that groups skills with related agents and commands; and an entire repository/marketplace. Wshobson's skill-only route explicitly leaves agents and commands behind, while plugin install brings all components within the selected plugin. This supports maintaining a dependency-aware component catalog and the approved curated-bundle and individual selectors. A source repository's directory layout is not by itself sufficient metadata to infer dependency closure or ownership.

### Transport, symlinks, and operating systems

Skillet reports broad source transports and packages its CLI as a static binary for listed macOS, Linux, and Windows targets. Those are properties of Skillet's independently maintained Rust resolver and packaging pipeline. They are not a low-cost extension of a Python stdlib installer, and its documented scope is skills alone. A repo that already commits the selected runtime assets needs no external resolver during teammate setup. Keep archive, OCI, and generalized remote-source support as later options only if a concrete distribution need requires them.

Symlinks enable source edits to appear immediately in client skill directories, but they couple installation to filesystem and OS behavior and make the destination a view of a source tree rather than an owned copy. Skillet's changelog listing both symlink and copy fallback suggests an implementation pattern worth considering for local-development mode, not a reason to replace committed copies. No source here shows that symlinks are portable or acceptable for all client/Windows configurations.

### Version, maintenance, and license evidence

Observed release evidence: skills-lock publishes no release on its repository page and explicitly labels itself a prototype; Superpowers' plugin manifest says 6.4.2 and MIT; Skillet's releases page identifies v1.1.0 / commit `ac839a9`, dated 2026-06-20, with Apache-2.0 stated in its README. Wshobson/agents has active-looking public history through the visible 2026-09-01 `a30778f` entry, describes its large catalog on `main`, and states MIT; the root README does not claim a release version. These are observed upstream snapshots, not recommendations to adopt any dependency. Repository license metadata does not by itself establish the license/provenance of every third-party asset a consumer may copy; verify individual imported content before vendoring.

## Primary sources

- [skills-lock README](https://github.com/luisalima/skills-lock) (lock semantics, security boundaries, maturity, license)
- [Superpowers README](https://github.com/obra/superpowers/blob/main/README.md), [plugin manifest](https://github.com/obra/superpowers/blob/main/.claude-plugin/plugin.json), [porting guide](https://github.com/obra/superpowers/blob/main/docs/porting-to-a-new-harness.md), and [visible commit history](https://github.com/obra/superpowers/commits/main)
- [wshobson/agents README](https://github.com/wshobson/agents), [usage guide](https://github.com/wshobson/agents/blob/main/docs/usage.md), [marketplace manifest](https://github.com/wshobson/agents/blob/main/.claude-plugin/marketplace.json), [MIT license](https://github.com/wshobson/agents/blob/main/LICENSE), and [visible commit history](https://github.com/wshobson/agents/commits/main)
- [Skillet README](https://github.com/echohello-dev/skillet), [v1.1.0 changelog](https://github.com/echohello-dev/skillet/blob/main/CHANGELOG.md), [release page](https://github.com/echohello-dev/skillet/releases), and [Apache-2.0 license](https://github.com/echohello-dev/skillet/blob/main/LICENSE)

## Verification limits

This was source review only. No repository was cloned, installed, built, or executed, and no client compatibility claim was tested. GitHub Contents API access was attempted for repository metadata but failed for three of the four endpoints in the available browser; paths were then selected from each repository's own GitHub file navigation, search result, or changelog. The observed short SHAs are those exposed by GitHub commit/release pages. The skills-lock page exposed its commit count but not its latest SHA, so no current SHA or release version is claimed for it. Skillet's README makes inconsistent implementation-status claims, recorded above rather than resolved by inference.
