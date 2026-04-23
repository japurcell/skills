---
work_id: WORK_ID
phase: clarification
status: complete
updated_at: ISO8601_TIMESTAMP
depends_on: [research]
---

# Clarifications: TITLE

<!-- One entry per question that required human input or a stated assumption. -->
<!-- Questions fully resolved by research alone do not need entries here. -->

## q3 — QUESTION_TEXT

- **blocking**: true | false
- **status**: answered | assumption | unanswered
- **asked_at**: ISO8601_TIMESTAMP
- **answered_at**: ISO8601_TIMESTAMP
- **answer**: Human's answer, or "N/A" if assumption.
- **assumption**: *(if status is assumption)* The assumption taken and its rationale.

---

## q4 — QUESTION_TEXT

- **blocking**: false
- **status**: assumption
- **assumption**: "Description of assumption taken and why it is reasonable."

---

<!-- Add one entry per question. Questions with status: unanswered and blocking: true block Gate C. -->
