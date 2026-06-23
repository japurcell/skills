def format_row(row):
    owner = row["owner"].strip()
    amount = str(row["amount"]).strip()
    return f"{owner},{amount}"
