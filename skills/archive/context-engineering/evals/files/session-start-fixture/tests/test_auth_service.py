from src.auth_service import session_timeout_minutes


def test_session_timeout_minutes() -> None:
    assert session_timeout_minutes() == 15
