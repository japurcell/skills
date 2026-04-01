# Run Note — Eval 3, Old Skill Baseline, Run 1

**Track selected:** Standard (medium-sized, 3 files, explicit review request)

**Key observations:**

- The old skill enforces implementation via the "Do not create artificial approval gates" directive in Phase 5 — it is a strong push-forward signal.
- Quality review is enforced by "Always run independent code-reviewer agents… on every track" in Phase 6 — the word "always" is unconditional.
- TDD is enforced the same way: "Always use the tdd skill" with no per-track escape.
- Standard Track quality review uses 3 parallel `code-reviewer` instances: simplicity, correctness, conventions.
- The skill names the agent file explicitly (`agents/code-reviewer.md`) but does not enumerate required focuses in a fixed list — they are examples ("such as simplicity, correctness, and conventions"), leaving some interpretation to the executor.
- No handoff artifact was produced since scope is bounded.
