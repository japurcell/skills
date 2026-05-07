- Deduped review scope (files): skills/build-review/SKILL.md, skills/build-review/implementer-prompt.md, notes.txt
  (exclude deleted scratch.tmp and exclude .gitignore)

- Number of code-reviewers: 1 (single reviewer run is sufficient for this small change)

- Context to send to reviewer before updating tracking:
  1. Touched files list (above) and git status --porcelain lines: M skills/build-review/SKILL.md, M skills/build-review/implementer-prompt.md, ?? notes.txt (deleted and .gitignore excluded).
  2. Current verification context: implementer returned DONE (include whatever verification commands/output they reported) and code-simplifier returned DONE (no unresolved concerns).  
  3. Instruction to follow code-reviewer-prompt.md template and to NOT commit; update tracker only after reviewer returns DONE.
