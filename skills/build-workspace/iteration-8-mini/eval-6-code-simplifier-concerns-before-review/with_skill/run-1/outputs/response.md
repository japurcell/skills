Follow the skill: read the simplifier's concerns, then treat this as unresolved work — do NOT update tracking or proceed to reviewers. Re-dispatch the implementer (owner of the change) with a lean handoff that includes:
- the exact concern text and affected files,
- success criteria (narrow helper scope OR restore prior behavior),
- required verification (add focused unit/regression tests that fail before fix, run test command),
- validation commands and file hints.
After the implementer returns DONE, re-run code-simplifiers, then reviewers, then update tracking.
