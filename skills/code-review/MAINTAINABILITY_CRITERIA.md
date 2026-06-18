# Maintainability Criteria

The Maintainability agent performs a strict maintainability review. Prefer deleting complexity over rearranging it. Favor a small number of high-conviction structural findings over cosmetic notes.

## Presumptive blockers unless clearly justified

Treat these as presumptive blockers when introduced by the reviewed change:

- file growth from under 1000 lines to over 1000 without strong justification
- unjustified file-size explosions
- spaghetti growth
- unnecessary abstraction layers
- logic in the wrong layer
- obvious duplication of canonical helpers
- cast-heavy contracts that obscure invariants
- generic mechanisms hiding simple data-shape assumptions

## Aggressively flag

Flag changes that introduce or worsen:

- ad-hoc conditionals
- one-off booleans
- nullable modes
- flags that complicate control flow
- unnecessary wrappers
- unnecessary casts
- unnecessary optionality
- unnecessary indirection
- `any`, `unknown`, or ad-hoc object shapes that obscure invariants
- hacky or magical behavior
- duplication of canonical helpers
- copy-pasted logic instead of extracted helpers
- narrow edge-case handling inserted into an already busy function
- sequential orchestration or non-atomic updates when a cleaner structure is obvious
- logic placed in the wrong file, module, layer, or abstraction boundary

## What to prefer

Prefer findings that identify a simpler structure, such as:

- deleting a wrapper
- moving logic to the layer that owns the invariant
- replacing mode flags with explicit types or separate flows
- using an existing canonical helper
- collapsing unnecessary generic machinery into direct code
- making invalid states unrepresentable
- splitting a bloated function or file only when it reduces conceptual complexity

## Do not flag

Do not flag maintainability issues that are only:

- personal style preferences
- naming preferences without material comprehension impact
- cosmetic rearrangements
- refactors unrelated to the reviewed change
- issues that tooling should catch
