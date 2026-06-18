def next_delay(attempt):
    return min(2 ** attempt, 8)
