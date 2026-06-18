from src.payment_retry import next_delay


def test_next_delay_caps():
    assert next_delay(4) == 8
