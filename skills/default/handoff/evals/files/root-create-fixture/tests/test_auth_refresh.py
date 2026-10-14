from src.auth_refresh import build_retry_schedule


def test_refresh_retries_backoff():
    assert build_retry_schedule() == [0.5, 1.0, 2.0]
