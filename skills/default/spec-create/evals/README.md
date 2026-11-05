# Evaluating spec-create

For each case in `evals.json`, create two fresh project directories. Copy the contents of the matching fixture project into each, preserving its layout. For the new-product case, leave both projects empty. Keep the inputs unchanged for future runs.

Give independent agents the same prompt and write boundary. One uses the exact `spec-create/SKILL.md` under evaluation. The other receives no spec-authoring skill. Keep the rubric, other runs, and their outputs out of both agents' context. Have each return its final response, including any open question or evidence of exercising a public entry point.

Compare each project's files with its starting fixture. Verify the destination and inspect every changed file. For the existing feature, check the run evidence against the real entry point. Grade the assertions against the spec and the response together. For the revision, distinguish an unresolved conflict from intentionally permitted variation.

Keep generated projects, grading evidence, and benchmark results in a temporary directory or sibling `spec-create-workspace/`, outside the maintained skill.
