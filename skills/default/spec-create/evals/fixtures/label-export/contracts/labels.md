# Label export

## Exported rows

The export returns one row per distinct label in first-seen order. The public JSON field `label` contains the original spelling. An empty collection returns an empty list.

## Conformance

- Exporting an empty collection returns `[]`.
- Exporting two occurrences of `Blue` returns one row with `"label": "Blue"`.
