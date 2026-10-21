# Asset Lifecycle

## Current Contract

The active metadata record is the authority for asset identity and owner approval.
Maintain this rule when planning recovery. Historical metadata is evidence only.
Create bounded assignments with full negative cases and a final integration proof.
This is a self-contained planning fixture. No real installer or account is involved.

## Requirements

- Publish an asset only after explicit owner approval; preserve its identity metadata.
- Recover after interruption before or after publishing without duplicate assets.
- Repeated recovery must preserve the same identity and metadata.
- Refuse conflicting identity metadata instead of overwriting an existing asset.
- A missing authority record blocks recovery; leave the state unfinished.
- First resolve whether recovery uses a transaction or an idempotency key. Record the decision before implementation depends on it.
- The final integration proof exercises approved publication, interruption, repeated recovery, conflict refusal, and missing authority against the shared identity invariant.

## Verification

This paper fixture has no project runtime or typecheck command. Mark automated
checks unresolved with that reason rather than inventing commands. A required
manual check reads the task manifest and records a requirement-to-task mapping.
Integration verification remains unresolved until the implementation environment
and commands are supplied. Unresolved checks cannot establish completion.

## Assignment Review

Each assignment carries the current contract and relevant requirements as source
or context references. Explain entry state, full completion proof, prerequisites,
and any stopping boundary. Explain why indivisible recovery stays together when
its partial steps cannot preserve the identity invariant independently.
