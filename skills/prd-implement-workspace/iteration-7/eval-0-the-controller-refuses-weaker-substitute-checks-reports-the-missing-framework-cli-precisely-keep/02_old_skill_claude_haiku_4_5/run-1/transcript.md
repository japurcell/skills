**Skill used:** `/home/adam/dev/personal/skills/skills/prd-implement-workspace/skill-snapshot/SKILL.md`

**Scenario:** W2 lowest-open wave, child #5101 with AFK status and no blockers. Implementation and review complete. Verification has two steps: one passes (`pnpm test`), one fails (`pnpm exec expo-router verify` missing CLI). Subagent proposes static analysis substitute.

**Reasoning:**
1. SKILL.md lines 243 (stop condition: required verification command unavailable) and 265 (do not downgrade framework CLI to static analysis)
2. Subagent proposal violates explicit rule: framework CLI cannot be replaced unless child issue lists alternative
3. Controller response: reject substitute, name missing `expo-router` CLI, keep #5101 open, parent line remains `[ ]`, stop before next wave
4. Response format follows SKILL.md section "Final response" with all required section structure
