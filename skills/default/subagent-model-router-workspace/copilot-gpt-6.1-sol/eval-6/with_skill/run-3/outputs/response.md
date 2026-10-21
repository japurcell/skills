Router returns complete structured decision: `dispatchable`, `tier`, exact `model`, exact `reasoning_effort`, `reason`, `escalation_trigger`, and same-tier `fallback` or `none`.

Caller controls storage and presentation. That separation never permits implicit values: dispatch must explicitly apply both validated model and effort.
