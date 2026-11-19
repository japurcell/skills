# T5a, freeze the rollout fixture

The hook maintainer takes the decoded commands and owned metadata from `069b3f22` using `git show REV:PATH`. The repository sources are `.github/hooks/hooks.json`, `.gemini/settings.json`, and `.codex/hooks.json`. The portable documents are `skills/default/brain-install/assets/hooks/{copilot,gemini,codex}.json`. Each scope has two events and ten command strings (Copilot four, Gemini two, Codex four). Save literals in an independently maintained test fixture under `scripts/tests/hooks/`. Stop after the fixture matches all six original documents.

The hook maintainer owns only the independent six-document fixture and its check. Inspect raw blobs at 069b3f22. Freeze 20 command strings and all owned metadata. Run a comparison through the public generator fixtures. Stop before changing generation or writing configurations.

Use the [milestone contract and verification commands](5-project-launchers.md) and the [integration plan](../ExecPlan.md). Record results and remaining evidence here.
