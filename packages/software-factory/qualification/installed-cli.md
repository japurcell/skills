# Installed CLI and skill qualification

An installed `dist/cli.js` is identified only by its canonical module path under the repository's Git-common `factory/install/runtime`. Before command dispatch, it checks the completed-install receipt hash against the unique SQLite completion event through an existing-only read-only connection. Schema 7, repository ID/release/readiness and the absence of a maintenance claim must match. Ordinary runner and dashboard claims remain valid. The marker must already be absent. The operation-bound publication intent, candidate receipt, moved subtree identities and complete file/mode inventories are rechecked at their published locations. The release manifest, Node archive digest and omission list, pinned running Node path/version, toolchain lock, and selected external provider descriptors are checked before adapters are constructed. User-editable `.factory` authoring files are not pinned to their initial bytes on ordinary startup.

The CLI binds only selected qualified Codex and Copilot descriptors. Codex's selected modes further restrict its adapter; Copilot remains read-only. Explicit native environment keys are passed to those adapters without reading credentials. The installed sender is passed to invocation and dashboard reminder paths. The native command-only case leaves success notices and reminders disabled and makes no desktop or provider call. Development CLI execution remains unbound.

The public Python `verify`, `prepare` and `install` routes accept `--providers` with a bounded descriptor file selecting only the already qualified external Codex/Copilot artifacts and modes. The separate no-call selected-provider installation proof validates binding without starting either provider. Selected-provider live execution remains a separate qualification boundary.

Run the archive-free focused test after building:

```sh
node --test test/installed-bindings.test.mjs
```

Run the explicit native Darwin arm64 or Linux x64 test with the exact archive, Python 3.13.14 and copied offline cache present. Actions exports the selected archive; the cache seed is runner-private and populated by its locked dependency acquisition:

```sh
FACTORY_TEST_PYTHON=/absolute/python3.13 FACTORY_TEST_NODE_ARCHIVE=/absolute/pinned-node.tar.xz FACTORY_TEST_NPM_CACHE_SEED=/absolute/cache node --test qualification/installed-cli-native.qualification.mjs
```

The native test hard-fails if a prerequisite is absent. It performs public Python first install, then invokes an authored command-only TypeScript workflow and reads its saved history through the installed Node and CLI. It checks mode-specific installed help, default disabled notification preferences, no unselected adapter, preserved customized authoring, an unselected provider's refusal before launch, changed published compiled bytes refused at CLI startup, unchanged dirty source/index and shared cache, direct pinned toolchain commands, and completed stage cleanup. No provider/model or notification delivery is attempted. Native run39884556274 at5ce97654 passes the installed proof on Linuxx64 in40.661seconds and Darwinarm64 in51.836seconds, alongside complete foundation passes. Artifacts are retained at `/tmp/factory-native-foundation-39884556274/`. Newer source composition still needs its current proof. Native Windows installed startup, selected-provider live execution, and broader maintenance operations remain unqualified. Acceptance review remains pending with the other implementation nodes.
