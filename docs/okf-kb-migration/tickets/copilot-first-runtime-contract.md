# Copilot-First Runtime Contract

**Type:** grilling
**Status:** closed
**Blocked By:** copilot-cli-integration-surfaces.md
**Research Dir:** N/A

## Question

Should the primary rollout preserve the standard Copilot CLI experience through a repository extension with atomic legacy fallback and an explicitly weaker `advisory_stop` assurance, require a separate SDK-hosted interface to retain pre-model hard stops, or wait for a native Copilot prompt-admission capability; and what exact privacy, tool-denial, capability-test, and fallback contract follows from that choice?

---

<!-- Resolution will be appended here -->

## Accepted round 1

The user selected the standard Copilot CLI project-extension boundary. The primary adapter will run inside the normal interactive CLI through the bundled extension SDK, perform deterministic per-submission context selection, use atomic legacy fallback, and deny tools while unsafe state is active. The contract will describe any inability to prevent first-model inference or text output as `advisory_stop`; it will not claim a host-enforced `hard_stop`.

A separate SDK-hosted interface is not part of the primary migration, and the rollout will not wait for a future native prompt-admission hook.

## Accepted round 2

- Use `use_legacy` for projection or selector failures when trustworthy legacy state is available. Use `advisory_stop` plus deny-all-tools for pending or indeterminate ingest, invalid enabled configuration, access or workspace validation failures, and failed legacy loading. Missing extension support leaves the repository unenrolled on its existing legacy path. Never combine partial OKF and legacy context.
- Require the project extension to load successfully under Copilot's experimental mode and pass behavioral capability tests against every target CLI upgrade. A version string alone never enables OKF.
- Tasks requiring pre-inference denial or prompt confidentiality are outside the standard Copilot CLI contract. This migration will not build a separate SDK host.
- Correction to the proposed Gemini scope: Gemini remains a fully supported OKF provider for now. The migration retains its adapter, tests, and rollout rather than reducing it to untouched legacy compatibility.

## Accepted round 3

Copilot reaching `default` defines completion of this migration. Gemini remains fully implemented, tested, and independently promotable through its own shadow, canary, and default ladder, but a Gemini-specific failure does not block Copilot promotion. A defect in the shared profile, projection, selector, legacy loader, or other provider-neutral contract blocks every enrolled provider.

## Accepted round 4

- Implement the shared runtime and both provider adapters before the first production promotion. Promote Copilot first; Gemini follows through an independent ladder whose observation windows and provider-specific failures do not delay Copilot.
- Require byte-identical provider-neutral behavior for normalized inputs, selected concepts, ordering, rendered context, lifecycle handling, legacy fallback, reason codes, and privacy-safe audit data. Permit only documented host differences: Copilot uses `advisory_stop` plus tool denial, Gemini enforces `hard_stop`, and their JSON envelopes and injection mechanics differ.
- After Copilot becomes default, every shared profile, producer, selector, runtime, and evaluation change must continue passing Gemini adapter and cross-provider parity tests. Gemini uses independent promotion evidence and rollback. Removing Gemini support requires a separate future decision.

## Final confirmation

The user confirmed the complete contract without further changes.

## Resolution

Make GitHub Copilot CLI the primary provider through a repository-scoped project extension using the CLI-bundled SDK and `onUserPromptSubmitted`. Enrollment requires experimental extension support plus behavioral capability tests for the actual target build. Use atomic legacy fallback for recoverable projection and selection failures; use `advisory_stop` plus deny-all-tools for unsafe or indeterminate state. Never claim that standard Copilot CLI prevents first-model inference or text output, and keep strict pre-inference tasks and a separate SDK host outside this migration.

Keep Gemini fully supported with its existing enforceable `hard_stop` contract. Implement both adapters before promotion, require exact provider-neutral parity except for documented enforcement and envelope differences, promote Copilot first, and give Gemini an independent rollout and rollback ladder. Copilot reaching `default` completes the migration; Gemini-specific failures do not block Copilot, while shared-core failures block every provider. Continue Gemini tests and parity obligations until a separate future decision removes its support.
