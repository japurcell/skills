## Summary

Summarise which questions required human input and which assumptions were taken to keep the workflow moving.

## q3 — QUESTION_TEXT

- **blocking**: true | false
- **status**: answered | assumption | unanswered
- **asked_at**: ISO8601_TIMESTAMP
- **answered_at**: ISO8601_TIMESTAMP
- **answer**: Human's answer, or `N/A` if assumption.
- **assumption**: *(if status is assumption)* The assumption taken and its rationale.

---

## q4 — QUESTION_TEXT

- **blocking**: false
- **status**: assumption
- **assumption**: "Description of assumption taken and why it is reasonable."

---

## Machine Data

```yaml
work_id: WORK_ID
kind: phase
phase: clarification
status: open
depends_on:
  - research
```
