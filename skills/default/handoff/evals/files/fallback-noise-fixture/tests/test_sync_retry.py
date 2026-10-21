from src.sync_retry import should_retry


def test_retry_stops_at_limit():
    assert should_retry(3, 3) is False
