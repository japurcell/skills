# Build and Release

When changing deployment settings, obtain explicit approval before applying them. Documentation-only changes are excluded.

Release procedure: run `python -m unittest discover -s tests` before publishing. Do not publish if checks fail.

The worker queue retries transient failures three times.
