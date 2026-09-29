# Evaluate ECC Ownership

**Type:** research
**Status:** closed
**Blocked By:** none
**Research Dir:** research/ecc-ownership

## Question

Which ECC ownership, selection, adapter, and migration practices should inform this repository's selective installer design? Verify current first-party documentation and source for ownership boundaries, checksums, modified files, conflict preflight, pruning, shared dependencies, config merges, profiles, migration, portable runtime paths, repair/uninstall, native packages, operating systems, and license. Compare each useful finding to the approved contract and distinguish useful patterns from mechanisms that violate it. Do not implement or execute an installer.

---

## Resolution

ECC's module catalog and per-operation install state are useful reference points: modules carry targets and dependency edges, while state records the requested and resolved modules, source version/commit, ownership, and per-file content hashes. Its stable-ID hook merge is a concrete semantic config ownership example.

The generic ECC installer is incompatible with the approved local-edit policy. It skips an existing unowned path and continues installing other operations, while successful updates replace files already marked managed even when locally edited. The Kimi guided adapter has stronger conflict preflight and revalidates state and destinations before writes, but multi-harness apply is sequential and can finish partially. Keep our whole-operation conflict-before-writes rule, and consider its operation classifications plus apply-boundary revalidation as implementation details. Selected-file pruning behavior was not verified, so the approved ownership, unchanged-content, no-longer-required gates remain authoritative.

Full source citations, version boundary, limitations, and comparison are in [ECC ownership findings](../research/ecc-ownership/findings.md). Research was static; ECC was not installed or executed.
