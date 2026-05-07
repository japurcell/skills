Plan the review as follows.

- Deduped review_scope_files (stable order): 
  1) skills/build-review/SKILL.md
  2) skills/build-review/implementer-prompt.md
  3) notes.txt

- Number of code-reviewers to run: 1 (<=5 files → single reviewer covers full list).

- Context to send to that reviewer (before updating tracking): the exact file list above; the implementer's verification context (which validation commands were run and their results / any assertions); the fact that the implementer and code-simplifier returned DONE; and the manager rule to exclude deleted files and .gitignore from scope.
