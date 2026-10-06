---
type: Known Issue
description: Known issues, quirks, and workarounds for `skills`.
---

# Skills - Known Issues

Layer-specific quirks for skills. Cross-cutting issues live in `.agents/memory/KNOWN_ISSUES.md`.

**Affected area:** `skills/*/SKILL.md`
**Description:** `python3 skills/skill-creator/scripts/quick_validate.py` rejects `disable-model-invocation` frontmatter even when a skill needs to keep it.
**Workaround:** Preserve the key when a human has approved it; expect validation to fail until the validator supports it.

**Affected area:** `skills/skill-creator/scripts/quick_validate.py`
**Description:** The validator requires the undeclared `PyYAML` package and fails with `ModuleNotFoundError: No module named 'yaml'` when it is unavailable.
**Workaround:** Do not install dependencies implicitly. Run it with the checked-in runtime: `PYTHONPATH=scripts/vendor python3 skills/skill-creator/scripts/quick_validate.py skills/<skill-name>`.

**Affected area:** Agent-brain status/doctor SQLite capability output.
**Description:** SQLite synchronous and fullfsync settings are connection-local. A read-only inspection can report synchronous `2` while mutation connections request and verify EXTRA (`3`); status does not change connection settings to imply durability.
**Workaround:** Interpret observed values with the reported access mode. The common-protocol fixture proves requested/observed mutation settings, not filesystem/VFS, OS-crash, or power-loss guarantees.

**Affected area:** Agent-brain bridge and registered stage JSON stdin.
**Description:** Ambient `PYTHONIOENCODING=cp1252` can silently corrupt non-ASCII source paths and provider IDs before JSON validation.
**Workaround:** Reconfigure stdin to UTF-8/strict at each public JSON input seam. Registered stages must validate invocation authority before configuring or reading semantic input. Preserve subprocess coverage with raw UTF-8 bytes and invalid UTF-8.

**Affected area:** Agent-brain configuration and durable numeric input.
**Description:** Python's JSON decoder raises a broader `ValueError` for integer digit limits; `math.isfinite` can raise `OverflowError` for a decoded oversized integer timestamp.
**Workaround:** Preserve decoder limits and report numeric-limit/range failures as structured invalid configuration. Bound durable time values before float conversion so status/doctor remain unavailable/incomplete and bridge recovery preserves damaged expected state.
