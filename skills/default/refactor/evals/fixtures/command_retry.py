from retry_policy import allowed


def run(attempt):
    return allowed(attempt)
