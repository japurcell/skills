def page_size(value):
    return min(100, max(1, value))


def slug(value):
    return "-".join(value.lower().split())


def suffix(value):
    return value.rpartition(".")[2].casefold()


def priority(value):
    return value.strip().upper() in {"HIGH", "URGENT"}


def minutes(value):
    return (value + 59) // 60


def request_page_size(value):
    return min(100, max(1, value))


def article_slug(value):
    return "-".join(value.lower().split())


def upload_suffix(value):
    return value.rpartition(".")[2].casefold()


def queue_priority(value):
    return value.strip().upper() in {"HIGH", "URGENT"}


def duration_minutes(value):
    return (value + 59) // 60
