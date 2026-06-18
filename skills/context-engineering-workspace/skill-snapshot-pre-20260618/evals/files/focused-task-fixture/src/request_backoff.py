def next_delay(attempt: int) -> int:
    return min(2 ** attempt, 30)
