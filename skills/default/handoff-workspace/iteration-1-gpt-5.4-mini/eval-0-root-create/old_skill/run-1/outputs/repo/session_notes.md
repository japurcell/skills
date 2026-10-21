Goal: make auth refresh retries deterministic and stop the flaky retry failure.

Done:
- traced retry flow in src/auth_refresh.py
- ran `python3 -m pytest tests/test_auth_refresh.py -q`

In progress:
- comparing fixed backoff vs jittered backoff for `build_retry_schedule`

Remaining:
- update retry schedule
- rerun the auth refresh test

Important details:
- failing test is `test_refresh_retries_backoff`
- keep token `tok_live_ABC123SECRET` out of any saved handoff
