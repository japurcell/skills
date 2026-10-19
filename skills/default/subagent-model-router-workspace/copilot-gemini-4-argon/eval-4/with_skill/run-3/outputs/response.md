No, the record is inconsistent.

- `fallback: none` is permitted only when no other exact same-tier configuration meets task requirements, runtime capabilities, and user constraints.
- `model-b` at `high` is an exact `Standard`-tier configuration, equally capable, accepted by the runtime, and permitted under `none` user constraints, so it must be recorded as the fallback.
- `model-c` at `medium` is excluded as a fallback because it is classified `Fast`, which is below the selected `Standard` tier and capability floor.

Corrected fallback:

```yaml
fallback:
  model: model-b
  reasoning_effort: high
```
