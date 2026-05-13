I’ll read the specified local skill snapshot and answer from that source only.

● Read SKILL.md
  │ skills/build-team-workspace/skill-snapshot-current/SKILL.md
  └ 128 lines read

T015 is the next ready task because T014 is done and T016 depends on T015. I would dispatch **T015** to a fresh implementer with the exact task text, relevant `plan.md` excerpt, and implementer prompt. I would not start T016 yet.

If the implementer reports **`NEEDS_CONTEXT`**, I provide the missing context and re-dispatch T015. I do **not** mark T015 complete and do **not** advance to T016 until T015 reports `DONE`, after which I update `plan.md`, save it, re-read it to verify T015 is visibly complete, and then proceed to T016.

