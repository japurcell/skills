# Maintainability Criteria

Run a strict maintainability review. Prefer deleting complexity over rearranging it. Report only high-conviction structural issues introduced or worsened by the change.

## Presumptive blockers

Flag unless clearly justified:

- file growth from under 1000 lines to over 1000
- unjustified file-size explosion
- spaghetti growth
- unnecessary abstraction layers
- logic in the wrong layer
- duplication of canonical helpers
- cast-heavy contracts that hide invariants
- generic mechanisms hiding simple data-shape assumptions

## Also flag

- ad-hoc conditionals, one-off booleans, nullable modes, or control-flow flags
- unnecessary wrappers, casts, optionality, or indirection
- `any`, `unknown`, or ad-hoc object shapes that hide invariants
- hacky or magical behavior
- copy-pasted logic instead of existing/extracted helpers
- narrow edge-case handling added to an already busy function
- non-atomic or sequential orchestration where a simpler structure is obvious
- logic in the wrong file, module, layer, or abstraction boundary

## Prefer fixes that

- delete wrappers
- move logic to the owner of the invariant
- replace mode flags with explicit types or separate flows
- use canonical helpers
- collapse generic machinery into direct code
- make invalid states unrepresentable
- split bloated functions/files only when it reduces conceptual complexity

## Do not flag

- personal style preferences
- naming preferences without material comprehension impact
- cosmetic rearrangements
- refactors unrelated to the reviewed change
- issues tooling should catch
