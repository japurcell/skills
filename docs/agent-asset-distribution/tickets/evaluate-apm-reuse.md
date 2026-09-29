# Evaluate APM Reuse

**Type:** research
**Status:** closed
**Blocked By:** none
**Research Dir:** research/apm-reuse

## Question

Can Microsoft APM replace or provide a reusable dependency, provenance, or installation component while satisfying the approved distribution contract? Verify current first-party documentation and implementation for committed payloads, team/local/personal scopes, all required clients and asset types, immutable content verification, branch updates and preview, preservation of local edits, conflicts before writes, unchanged-owned pruning, configuration ownership, interrupted-operation recovery, runtime requirements, and license. Distinguish documented promises, inspected code, and unexecuted behavior. Identify exact gaps and whether wrapping APM would duplicate its lifecycle responsibilities.

---

## Resolution

Do not use Microsoft APM as the initial installer or a narrow dependency/provenance runtime for the approved contract. APM's current model resolves transitive packages from `apm.yml` across remote repositories, while this repository needs a curated catalog and required-dependency closure within one maintained source repository. APM can generate committed multi-client output and provides useful commit/hash provenance, frozen installs, preview, hash-gated pruning, and a committed-output CI audit. Its latest release at research time was v0.32.0 (`f0509d7`), MIT licensed, with standalone binaries available for macOS, Linux, and Windows. See the [full findings](../research/apm-reuse/findings.md).

The deciding gap is the approved write contract. APM populates its managed set from lockfile `deployed_files`, then treats those paths as non-collisions without checking local bytes. Its CI guide confirms an ordinary install overwrites modified managed output before audit. Unowned authored-path collisions are instead skipped or warned per path during integration, not rejected by a whole-operation preflight before any writes. APM's transaction explicitly excludes native target integrations from rollback. See [`pipeline.py`](https://github.com/microsoft/apm/blob/main/src/apm_cli/install/pipeline.py#L645-L719), [`BaseIntegrator.check_collision`](https://github.com/microsoft/apm/blob/main/src/apm_cli/integration/base_integrator.py#L167-L206), [`InstallTransaction`](https://github.com/microsoft/apm/blob/main/src/apm_cli/install/transaction.py#L69-L88), and the [committed-payload CI guidance](https://microsoft.github.io/apm/enterprise/enforce-in-ci/#audit-only-ci-pattern).

Wrapping APM to preflight all transformed files and merged config, preserve local edits, detect conflicts, and own safe pruning would duplicate much of the safety lifecycle while APM continues to own package resolution and deployment. Build the narrow repository-local catalog/materializer. Borrow APM's explicit ownership references, per-file hashes, hash-gated pruning, and target-specific merge patterns. Consider a read-only CI verifier for missing or hash-drifted committed outputs as a design refinement; this research does not amend the closed contract. No APM command or installer was executed, and source links were inspected on `main`, not a tag-pinned checkout.
