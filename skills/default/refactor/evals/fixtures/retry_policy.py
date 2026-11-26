from retry_limit import maximum


def allowed(attempt):
    return 0 <= attempt < maximum()
