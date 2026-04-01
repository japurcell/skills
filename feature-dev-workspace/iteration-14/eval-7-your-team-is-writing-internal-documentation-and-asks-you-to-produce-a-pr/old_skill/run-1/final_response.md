## Phase 6 Reference Card — feature-dev Workflow

> Source: feature-dev skill, Phase 6 specification
> Audience note: Follow this card literally. Steps listed here are what the workflow mandates — nothing added, nothing omitted.

---

### Phase 6 Goal

> "Ensure code is simple, DRY, elegant, easy to read, and functionally correct."

---

### Required Sequence

| Step | Action                                                  | Subagent role         | Track scaling                                                                                   |
| ---- | ------------------------------------------------------- | --------------------- | ----------------------------------------------------------------------------------------------- |
| 1    | Launch independent quality review agent(s)              | `code-reviewer`       | Light: at least 1 agent; Standard/Deep: multiple agents in parallel with differentiated focuses |
| 2    | Consolidate findings and prioritize issues              | (you, not a subagent) | —                                                                                               |
| 3    | Fix obvious high-severity issues directly               | (you, not a subagent) | Unless user asked to stop after review                                                          |
| 4    | Surface remaining risks, trade-offs, and follow-up work | (you, not a subagent) | —                                                                                               |

---

### Subagent mandate by track

**Light track:**

- At least one independent `code-reviewer` agent

**Standard track:**

- Multiple independent `code-reviewer` agents in parallel
- Each agent given a different focus: e.g., simplicity, correctness, conventions

**Deep track:**

- Multiple independent `code-reviewer` agents in parallel
- Each agent given a different focus: e.g., simplicity, correctness, conventions

---

### What "independent" means

Each `code-reviewer` agent is launched without seeing the findings of other reviewer agents. Independence is what prevents one agent's framing from suppressing coverage in a different area.

---

### What this card does not include

Steps not specified in Phase 6 of the workflow are not listed here. This card reflects the workflow as written.
