# Install candidate preparation qualification

The explicit `install.py prepare` route authenticates the complete selected release and pinned Node archive before executing `dist/install-entry.js` from a private copy. The Node entry accepts only a canonical, private 64-KiB request, revalidates the copied bundle, archive, extracted Node tree, and original source, then obtains the repository's existing bootstrap claim. It creates an absent-only candidate and a small controller stage, measures both, and binds their compact identities through one claim/token/phase transaction. Python reports a fixed public receipt only after its preparer process group closes and its exact temporary stage is cleaned.

The candidate receipt is separate from the 8-KiB bootstrap marker and handoff ticket. Its scan includes directories, empty directories, regular file bytes and modes, and refuses links, hard links, case collisions, unsafe names, special files, changed identities, extras, and changed receipts. It is bounded to 8,192 entries, 512 MiB total regular bytes, 128 MiB per file, 512 UTF-8 bytes per path, 32 components, and 8 MiB before JSON parsing. The controller payload still uses the existing 512-file/256-MiB stage limit. A bound candidate is checked during inspection, handoff and reclaim, including the `preparing` phase; an unbound partial candidate is preserved and refuses reclaim.

The fresh toolchain uses the candidate's direct Node and npm CLI with `ci --ignore-scripts --no-bin-links`, the exact release lock, private empty npm configuration and home, and a Python-owned cache. Each fixed npm or self-check command must close its own POSIX process group before candidate binding; Python then proves its preparer group closed before public success. The optional offline seed is copied with a bounded no-follow inventory and its source remains unchanged. Normal explicit mode can use npm's declared integrity-bound lock URLs; a normal network acquisition has not been qualified here. Selected provider bindings remain external and hash-bound; provider code, authentication and configuration are not copied into the candidate. Native Windows process lifetime, ACL and cross-language path equivalence are not qualified by the Darwin run.

The explicit macOS arm64 qualification requires Python 3.13.14, `/private/tmp/factory-node-v24.22.1-darwin-arm64-selection.tar.xz`, and `/tmp/software-factory-npm-cache/_cacache`. It hard-fails if any prerequisite is absent. From `packages/software-factory`, run:

```sh
FACTORY_TEST_PYTHON=/Users/adam/.pyenv/versions/3.13.14/bin/python3.13 rtk proxy node --test qualification/install-candidate-native.qualification.mjs
rtk proxy node --test test/install-candidate.test.mjs
rtk proxy node --test test/install-bootstrap.test.mjs
rtk proxy npm run test:release
rtk proxy npm run test:maintenance -- --operation controller
rtk proxy npm run typecheck
rtk proxy npm run build
```

The native qualification uses a disposable dirty Git repository and a private copy of the read-only offline cache. It checks the exact candidate and toolchain, the staged Node's self-check, unchanged source/index and cache seed, no install/toolchain publication targets, retained bootstrap marker, incomplete inspection, and one preparing claim. It also checks second-installer collision and candidate, stage, and source tampering. The measured pinned Darwin candidate contains 6,702 entries and 231,260,320 regular bytes; its controller payload contains 101 files and 123,533,377 regular bytes, both below unchanged caps. The stage's `maintenance-entry.js` deliberately refuses publication; the preparation receipt is not an installed-ready receipt. Handoff consumption, target moves, ready transition, marker unlink, and installed acceptance belong to the later publication operation.
