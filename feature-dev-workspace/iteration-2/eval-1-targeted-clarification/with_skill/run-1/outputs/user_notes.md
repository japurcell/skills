## Notes

- Grounding came from direct reads of the target skill, its helper agents, and adjacent planning skills in this repo.
- I intentionally did not inspect prior benchmark output contents so this run stays isolated from earlier responses.
- The most reusable repo patterns to borrow are the clarification discipline in skills/create-spec/SKILL.md and the artifact-oriented workflow in skills/create-plan/SKILL.md and skills/research/SKILL.md.
- The biggest product decision still needed is whether feature-dev should optimize more for fewer questions, stronger unfamiliar-repo discovery, or stronger handoff artifacts. The final skill shape changes depending on that priority.
- The helper prompts look generic enough that improving only skills/feature-dev/SKILL.md would likely leave some of the unfamiliar-repo weakness in place.
