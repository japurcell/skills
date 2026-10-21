# Evaluation scope and findings

Three offline prompts were run once per configuration. Both configurations passed all nine assertions on manual semantic review of saved responses. No quality advantage was demonstrated. The same supplied packet supported both configurations, so this does not measure source discovery, automatic triggering, or live PDF retrieval.

Each configuration used one isolated worker for its three cases. Cases within a configuration shared context; they are not independent model samples. The runtime did not expose per-case tokens, duration, or execution transcripts. Omitted metrics are unavailable, not zero.

The with-skill alignment response uses paraphrased section labels as locators. The substantive mappings are supported, but those labels should not be treated as verbatim headings. Review exact locators in live-source use.

The coordinator separately retrieved both Forest Service pages directly and opened the currently linked USDA framework PDF through the USDA delivery endpoint. That authoring evidence does not establish live retrieval behavior by evaluated agents.
