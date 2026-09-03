# Bundle Publication and Lifecycle

**Type:** grilling
**Status:** closed
**Blocked By:** none
**Research Dir:** N/A

## Question

What is the exact lifecycle contract for the generated OKF sidecar: its repository path, whether generated output is committed or ephemeral, how it is distributed to installed consumers, how freshness is proven, and what local rules govern reserved `index.md` and `log.md` files without case collisions?

---

<!-- Resolution will be appended here -->

## Resolution

The user accepted the following publication and lifecycle contract:

- Keep authored `.agents/instructions/` and `.agents/memory/` documents canonical. Publish their generated OKF v0.2 projection as a committed bundle rooted at `.agents/okf/`.
- Distribute the bundle with the repository checkout only. Consumers resolve it from the active workspace; installers must not copy project-specific KB content into global `~/.agents` storage.
- Commit `.agents/okf/.projection-manifest.json` with the canonical-input fingerprints and the OKF profile and generator identities needed to prove which inputs and producer contract created the projection. A deterministic regeneration-and-diff check is the authoritative repository freshness test.
- Treat a missing, invalid, or mismatched manifest as an unusable projection: emit an explainable diagnostic and fall back to the current loader. Preserve pending-source-ingest failures as separate hard gates. OKF concept lifecycle metadata does not replace projection freshness proof.
- Give the generator exclusive ownership of `.agents/okf/`. It performs a complete deterministic rebuild, prunes orphaned output, and emits no wall-clock-dependent content. Contributors invoke it explicitly after canonical KB changes; CI runs check mode. Installers, hooks, and runtime consumers never silently rewrite the committed bundle.
- Generate lowercase `index.md` at the bundle root and every included directory. Only the root index declares `okf_version: "0.2"`. Do not emit `log.md` initially.
- Never copy canonical `INDEX.md` or `LOG.md` into case-variant output paths. Reject every case-folded output collision, including collisions with reserved `index.md` and `log.md` names.
- Maintain one current bundle at the stable `.agents/okf/` path. Record the OKF, profile, and generator versions in its manifest; use Git history and release tags for rollback. A future incompatible format transition must deliberately choose a new path rather than silently changing this contract.
