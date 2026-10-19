**Choose the coordinator for local execution.**

The coordinator already has current context. One small edit and a known check cost less than context transfer, routing, startup, and handback review. No independent-review requirement offsets that overhead.

Correctness requirements remain unchanged: respect task scope, maintain exclusive ownership, perform the known check, retain evidence, and reconcile the plan.

Documentation work uses task-appropriate evidence. Do not invent product tests or source changes.

This choice minimizes expected completion cost, not merely model price. Delegation would add overhead without a stated correctness benefit.
