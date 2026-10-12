# Workflow authoring and task contract

**Type:** grilling
**Status:** open
**Blocked By:** confirmed-factory-requirements.md
**Research Dir:** not applicable

## Question

What is the smallest code-defined workflow contract that supports arbitrary workflow structure and both imported and agent-generated task graphs?

Discuss workflow definitions versus run data; custom stages, conditions, nesting, parallel work, and bounded loops; task identity, dependencies, acceptance criteria, and artifacts; plan import and ambiguity handling; and which invariants every custom step must honor.

Decide how much structure authors must declare so the UI can show planned work and dynamically discovered work. Consider plain TypeScript functions, a constrained builder, and configuration-driven recipes without assuming one is selected.

Resolution should include vocabulary, example contracts for the user's default workflow and one structurally different workflow, validation rules, and the chosen extension seam. Do not implement the runtime.

---

<!-- Resolution will be appended after this ticket is claimed and worked with the human. -->

