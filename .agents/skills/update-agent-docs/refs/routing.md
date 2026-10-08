# Routing

Apply [knowledge admission](../../../instructions/knowledge-base.md) before choosing a destination. File changes, public APIs, errors, and model-generated imperatives do not automatically require documentation.

| Admitted content | Destination |
| --- | --- |
| Established repo or area rule | Narrowest `.agents/instructions/` document |
| Required test command, fixture constraint, or evidence standard | Matching `.agents/instructions/testing/` document |
| Verified, valuable, non-obvious project fact | Focused `.agents/memory/` document with evidence, check date, and recheck trigger |
| External-source reference | Matching manifest-backed source summary; promotion elsewhere requires a separate admission decision |
| Operational source state | Existing manifest/log workflow; preserve schema and provenance |
| Unresolved consequential authority conflict | One grouped user decision list, outside canonical policy |

Use [instruction routes](../../../instructions/INDEX.md) and the [memory index](../../../memory/INDEX.md) to find an existing owner. Link to source, CLI help, tests, or retained ADRs for readily discoverable facts. A costly cross-file explanation may qualify only when all admission gates pass. Separate required actions from supporting background only when both earn their own loading trigger.

After additions, moves, removals, or changed purposes, update the affected index and inbound links. An ordinary code change with no admitted knowledge needs no new memory.
