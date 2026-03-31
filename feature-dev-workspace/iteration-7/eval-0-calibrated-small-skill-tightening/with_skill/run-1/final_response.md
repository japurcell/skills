Understanding
- Request is fully specified and bounded, so no blocking questions are needed.
- Proposed track: Light, with direct targeted edits.

Relevant Findings
- `skills/feature-dev/SKILL.md` description already says medium-to-large work, but can still be tightened by removing permissive trigger language.
- `skills/feature-dev/SKILL.md` already has a "When Not To Use This Skill" section; it can be shortened and moved earlier for better guardrail visibility.

Recommendation
- Tighten frontmatter description to trigger only when scope spans multiple files or meaningful architectural decisions.
- Keep exclusions explicit for tiny fixes, single-file edits, and straightforward fully specified work.
- Keep process calibrated (no unnecessary deep workflow for this edit).

Implementation Map
1. Update description in `skills/feature-dev/SKILL.md`.
2. Improve/shorten "When Not To Use" language in `skills/feature-dev/SKILL.md`.
3. Ensure wording stays aligned with track guidance.

Artifact Status
- Not required for this bounded same-turn request.
