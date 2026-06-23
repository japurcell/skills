from datetime import timedelta

REFRESH_WINDOW_SECONDS = 30


def should_refresh_token(expires_at, now):
    if expires_at is None:
        return False
    return (expires_at - now).total_seconds() <= REFRESH_WINDOW_SECONDS


def refresh_session(session, refresh_token, refresh_client, now):
    if not refresh_token:
        return {"status": "missing_token", "session": session}

    if session.get("expires_at") is None:
        return {"status": "missing_expiry", "session": session}

    if not should_refresh_token(session["expires_at"], now):
        return {"status": "fresh", "session": session}

    refreshed = refresh_client(refresh_token)
    updated = dict(session)
    updated["access_token"] = refreshed["access_token"]
    updated["expires_at"] = now + timedelta(seconds=refreshed["expires_in"])
    return {"status": "refreshed", "session": updated}
