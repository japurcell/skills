# Retry handoff

## Status

Linear backoff still needs replacement.

## Next step

Implement exponential backoff and then check staging.

## Prior results

OLD-RUN-741: on 2026-09-20, `python3 tools/retry_probe.py --fixture legacy --dry-run` passed 2 checks and reported `retries=2 total_delay_ms=300`. This handoff is the only retained copy of that result.

Retired parser lesson: legacy probe CSV files required semicolons; commas silently merged columns. That parser is no longer used, but the finding is unique historical evidence.
