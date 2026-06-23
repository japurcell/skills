from src.report_builder import build_report


def test_build_report_skips_blank_rows():
    rows = [
        {"owner": "Ada", "amount": "42"},
        {"owner": "", "amount": "9"},
        {"owner": "Grace", "amount": ""},
    ]
    assert build_report(rows) == "Ada,42"


def test_build_report_trims_owner_spacing():
    rows = [{"owner": "  Ada  ", "amount": "42"}]
    assert build_report(rows) == "Ada,42"
