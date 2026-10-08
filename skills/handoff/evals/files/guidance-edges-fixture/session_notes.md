# Latest retry session

Retry backoff implementation is complete. The next action belongs to the workspace owner: from the repository root, run `python3 tools/retry_probe.py --env staging --attempts 3 --timeout-ms 400` and record its result. The contributor must not run staging commands or change rollout settings. Staging acceptance remains unverified.

The last staging attempt produced the observed error `RetryProbeTimeout: request exceeded 400 ms`. DNS caching is a suspected cause, not a verified diagnosis. Current local evidence is in `reports/local-check.md`; it does not prove staging readiness.

A reusable rerun lesson remains relevant: clear the probe's local cache with `python3 tools/retry_probe.py --clear-cache` before repeating a failed local probe, because stale cache data can hide the failure. It does not change today's completed implementation decision.

If an owner-run staging probe fails again, the owner may restore the prior retry policy with `python3 tools/retry_probe.py --restore-snapshot snapshots/pre-retry.json`. Keep the snapshot for 30 days after failure. No restore has been performed.

Both retries and billing work have scratchpad folders. They are independent efforts. No staging action, production action, or implementation change is requested while preparing the next session's notes.
