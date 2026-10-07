from summary import summarize


ROWS = [7, 11, 13]


def main():
    result = summarize(ROWS)
    print(f"count={result['count']} total={result['total']}")


if __name__ == "__main__":
    main()
