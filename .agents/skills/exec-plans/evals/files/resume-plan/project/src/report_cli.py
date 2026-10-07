import argparse
import json

ROWS = [7, 11, 13]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    summary = {"count": len(ROWS), "total": sum(ROWS)}
    if args.json:
        print(json.dumps(summary))
    else:
        print(f"count={summary['count']} total={summary['total']}")


if __name__ == "__main__":
    main()
