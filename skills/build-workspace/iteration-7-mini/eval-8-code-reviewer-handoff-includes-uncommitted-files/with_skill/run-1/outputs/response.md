Send the code-reviewer a single dispatch containing:
- Touched files: skills/build/SKILL.md, skills/build/implementer-prompt.md
- Current verification context: the implementer’s verification steps, commands run, and results/output
- All uncommitted files from git status --porcelain, excluding deleted files and .gitignore: skills/build/SKILL.md, skills/build/implementer-prompt.md, notes.txt

(Exclude D scratch.tmp and .gitignore. Follow code-reviewer-prompt.md template when packaging.)
