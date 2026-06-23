from datetime import datetime, timedelta

from src.auth_session import refresh_session, should_refresh_token


def test_should_refresh_token_at_boundary():
    now = datetime(2026, 1, 1, 12, 0, 0)
    assert should_refresh_token(now + timedelta(seconds=30), now) is True


def test_refresh_session_handles_missing_token():
    now = datetime(2026, 1, 1, 12, 0, 0)
    session = {"access_token": "old", "expires_at": now + timedelta(seconds=5)}
    result = refresh_session(session, "", lambda _: {}, now)
    assert result["status"] == "missing_token"


def test_refresh_session_handles_missing_expiry():
    now = datetime(2026, 1, 1, 12, 0, 0)
    result = refresh_session({"access_token": "old"}, "refresh", lambda _: {}, now)
    assert result["status"] == "missing_expiry"
