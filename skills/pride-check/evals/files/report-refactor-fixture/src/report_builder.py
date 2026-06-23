from src.report_formatter import format_row


def build_report(rows):
    formatted = []
    for row in rows:
        if not row.get("owner"):
            continue
        if not row.get("amount"):
            continue
        formatted.append(format_row(row))
    return "\n".join(formatted)
