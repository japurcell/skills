# Metadata collection refusal diagnostics

The metadata collection wrapper may report one fixed `metadata-refused-*` marker when a collection fails. The marker distinguishes an outer process capture failure, an inner collector refusal, malformed or rejected wire, and an outer prerequisite failure. It carries no raw child output, paths, error text, or authority. A refusal still exits 1 and does not make metadata artifacts ready.

The wrapper checks the selected sources and input selection again before it releases a capture or wire marker. A failed check overrides the diagnostic with the generic prerequisite marker. The inner and outer process captures have independent deadlines; an outer deadline says nothing about the inner collector's outcome. The existing full metadata wire and artifact validation remain the only route to metadata artifacts, and SDK provenance remains a separate prerequisite.

Diagnostic capture and wire refusals return before artifact preparation. An existing failure while preparing an otherwise validated export can leave partial files in the private staging directory, but it emits only the generic prerequisite refusal and never signals readiness or uploads them.
