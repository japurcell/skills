# Review Existing Agent Asset Distributors

Research date: 2026-09-29. This is a recommendation for the user's decision, not an amendment to the [approved contract](tickets/choose-distribution-contract.md). Implementation remains on hold. Detailed evidence lives in [Evaluate APM Reuse](tickets/evaluate-apm-reuse.md), [Evaluate ECC Ownership](tickets/evaluate-ecc-ownership.md), and [Evaluate Distribution References](tickets/evaluate-distribution-references.md). The live decision is [Revisit Design After Existing Repositories](tickets/revisit-design-after-existing-repos.md).

## Recommendation

Keep the planned selective installer, committed copied payloads, one lifecycle engine, and native packages as a later additional channel. Add two focused refinements: an offline, read-only verification flag for committed installations, and an explicit line-ending policy for payload hashes and cross-platform clones. Most useful discoveries already correspond to requirements in the current [ExecPlan](../agent-asset-installer/ExecPlan.md), so they strengthen implementation evidence rather than require a new architecture.

The principal reason to retain our own narrow engine is lifecycle responsibility. Our dependency edges connect selected assets inside one maintained repository. APM resolves packages across repositories and manages their deployment. Adding a wrapper that separately owns all destination planning, edit protection, config ownership, pruning, and recovery would create overlapping lifecycle authorities. This is a design inference from the inspected behavior below, not a claim that APM cannot ever be extended.

## What changes the original research's interpretation

**APM can support committed outputs.** Its team workflow is not limited to committing a manifest and asking teammates to install. The official [audit-only CI guidance](https://microsoft.github.io/apm/enterprise/enforce-in-ci/#audit-only-ci-pattern) explicitly covers committed deployed files and verifies them without rewriting the checkout. That removes one apparent mismatch in the supplied research.

**APM still differs on edit protection.** The same guide states that ordinary `apm install` overwrites managed files before an audit. Source inspection separately shows managed paths bypass collision checks, while unowned authored collisions are skipped or warned during integration. These are distinct behaviors. The approved contract instead preserves local edits and stops the whole operation before destination writes on a conflicting update. APM's resolution transaction also excludes native target integrations. See [the APM findings](research/apm-reuse/findings.md) for corrected source anchors and limits.

**ECC's preservation guarantee is narrower than a general safe-update promise.** Its [v2.2.1 release notes](https://github.com/affaan-m/ECC/releases/tag/v2.2.1) confirm that successful upgrades still replace previously managed files; protections cover unowned collisions and failed-install hash checkpoints. Its Kimi-specific setup has stronger digest preflight and write-boundary checks, but can finish partially across harnesses. We should borrow catalog and semantic hook-ID patterns while retaining our approved edit and whole-operation conflict policy. Deselection pruning was not verified; see [the ECC findings](research/ecc-ownership/findings.md).

## Reference comparison

| Reference | Useful evidence | Effect on this design |
| --- | --- | --- |
| Microsoft APM | Committed-output audit, per-output hashes, shared owners, hash-gated pruning, update preview, distinct target schemas. | Keep these patterns. Do not adopt its deployment engine for the initial contract because edit, conflict, and recovery semantics differ. |
| ECC | Catalog/profile dependencies, source and per-operation state, stable IDs for owned hook config, write-boundary revalidation. | Use as concrete references for mechanisms already specified. Do not adopt managed-file overwrite or per-file skip-and-continue behavior. |
| skills-lock | Immutable commit plus content-tree digest; frozen install separates restoration from version updates. | Reinforces existing pin/digest/restore requirements. Frozen install still materializes files, so a proposed read-only verifier is a separate behavior. |
| Superpowers | Native distribution varies by client; recognized manifest fields determine what bootstrap/context files survive packaging. | Keep one authored source with explicit client adapters. Native package publication remains later. |
| wshobson/agents | Granular domain plugins, distinct skill-only routes, generated client outputs from canonical assets. | Reinforces bundles plus individual assets and canonical-to-native rendering. No requirement to regenerate assets during teammate cloning. |
| Skillet | Skills transport through Git, archives, local directories, and OCI; symlinks with copy fallback. | No initial transport or symlink expansion. Its skills-only scope differs, and README update maturity is inconsistent. |

The last four rows are supported by [the distribution reference findings](research/distribution-references/findings.md). Their own client lists and release tests do not establish this repository's future compatibility.

## Proposed refinement 1: verify committed payloads without repairing them

Add `status --check` to the existing public CLI rather than another lifecycle command. This proposed flag validates selection/lock coherence, schema and ownership records, installed file digests, and owned configuration values. It reports missing or changed managed content and exits nonzero on drift. It leaves payloads, settings, records, Git excludes, and refs untouched, makes no network request, and does not follow an upstream branch. A successful check means the installed bytes and owned values match the recorded installation, not that an upstream version is current or that a client has granted trust.

Record enough selection identity in the lock to detect a changed desired selection that has not been installed, such as a digest of canonical selection data. Compare only installer-owned config entries, not unrelated settings. Deliberate retained edits remain preserved by updates, but strict verification reports them as drift. Include a CI example that runs this check directly on the committed clone, before any restore or install. An install-first check could erase the difference it intends to detect.

APM's [audit-only pattern](https://microsoft.github.io/apm/enterprise/enforce-in-ci/#audit-only-ci-pattern) motivates this distinction. [skills-lock](https://github.com/luisalima/skills-lock) motivates immutable content verification, but its frozen install writes delivered files and is not a read-only audit. This proposed offline check compares installed content with recorded hashes; reconstructing output independently from pinned source is a separate check, as in APM's scratch-replay audit.

If accepted, update the public CLI/interface section and milestone 3 lifecycle acceptance in the ExecPlan, add a clone/CI case in milestone 6, and document the command in milestone 7. No tests or command implementation exist yet.

## Proposed refinement 2: make checkout line endings part of the payload contract

The plan records exact rendered hashes and requires clones to work on Windows, Linux, and macOS. Git may convert LF text to CRLF during checkout according to attributes and user settings. Consequently a byte-identical upstream selection can produce a false edited-file conflict after cloning, and shell launchers may need explicit LF. This is an inference from Git's documented conversion behavior, not a reproduced installer bug. See [Git's text and eol attributes](https://git-scm.com/docs/gitattributes#_checking_out_and_checking_in). APM's audit documentation explicitly normalizes line-ending-only hash differences, showing another possible policy.

Recommend preserving exact payload verification with a declared text/binary and line-ending policy. Use narrowly scoped, owned `.gitattributes` entries for team payload paths: LF for maintained text unless an asset explicitly requires CRLF, and no conversion for binary payloads. Preserve unrelated rules. Preflight conflicting existing attributes before any writes, and report unsupported overriding transforms rather than silently changing source or weakening hashes. Do not run repository-wide renormalization, change personal Git configuration, or normalize arbitrary whitespace while comparing edits.

Manage the attribute entries under the same semantic ownership and unchanged-only pruning rules as other configuration. Local and personal modes do not gain a reason to edit tracked team attributes. Validate fresh clones with `core.autocrlf` both enabled and disabled, exact recorded hashes, intact binary files, and working installed launchers. Asset-specific exceptions remain explicit.

If accepted, update catalog and owned-config descriptions, team installation and lifecycle acceptance, and native Windows/clone checks in the ExecPlan. This is a focused robustness refinement within the approved operating-system requirement, not a new transport or installation scope.

## Keep the existing boundaries

No external package dependency resolver, marketplace server, OCI support, symlink mode, uninstall command, or retained version history is needed for the first release. Current-recorded-revision restoration already supplies the intended repair behavior. Required dependency closure, per-file baselines, shared owner reconciliation, stable semantic config locators, preview, apply-time revalidation, and client discovery proof already appear in the plan. Clarify preview classifications and dependency reasons during implementation, without treating these existing requirements as new features.

Keep the approved clients and OS targets. Existing native package examples reinforce generating only recognized components from maintained sources; they do not warrant starting publication or assuming uniform client support. A future APM-compatible package can be evaluated as another generated distribution channel if a concrete consumer needs it, without making APM the initial runtime dependency.

## Evidence and decision state

Research inspected first-party documentation and targeted code. No third-party installer, APM/ECC command, package, or client was executed, and no real-home state changed. APM v0.32.0 and ECC v2.2.1 release evidence was checked; some implementation citations use moving `main`, with that distinction recorded in each findings file. Selected-file pruning in ECC and conflicting Skillet update maturity remain unverified. Source citations were corrected where web extraction indices had been mistaken for physical code lines.

The original contract and implementation design remain the baseline. The two refinements and recommendation to retain the architecture await the user's live response in [Revisit Design After Existing Repositories](tickets/revisit-design-after-existing-repos.md). Accepting a planning amendment will not lift the explicit implementation hold.
