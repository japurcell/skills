DEFAULT_TIMEOUT_MINUTES = 15


def build_session() -> dict[str, int]:
    return {"timeout_minutes": DEFAULT_TIMEOUT_MINUTES}
