Goal: ship tenant-scoped CDN invalidation for search.

Chronology:
- Oct 1: the work was limited to local TTL cleanup. The old next step was to rerun the local cache test.
- Oct 1: four retry attempts printed the same vendor cache stack trace; the full output is in `logs/purge-run-history.log`.
- Oct 7 owner update: scope changed after the previous handoff. The local TTL task is closed; finish CDN invalidation instead.

Current state:
- `src/cdn_purge.py` builds a request, but currently sends every tenant to the global region.
- `tests/test_cdn_purge.py` contains the tenant-isolation check.
- Review correction: the request must use the tenant's configured region.
- Durable rule: every purge request must remain scoped to its tenant; never fall back to a global purge.
- The focused CDN test has not been rerun after the current code change. The earlier local TTL pass does not verify this work.
- First inspect the request mapping, correct the region source, then run the focused CDN test.
