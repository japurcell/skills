# Payment sync

## Retry policy

When the vendor returns HTTP 429, `src/payment_sync.py` should retry with exponential backoff up to three times.

## Settlement

Settlement summaries are emailed once per day.
