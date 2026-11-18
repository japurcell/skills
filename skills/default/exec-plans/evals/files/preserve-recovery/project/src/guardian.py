import argparse
import shutil


def snapshot(source_path, snapshot_path):
    shutil.copyfile(source_path, snapshot_path)


def restore(snapshot_path, target_path):
    shutil.copyfile(snapshot_path, target_path)


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    rollback = subparsers.add_parser("rollback")
    rollback.add_argument("--snapshot", required=True)
    rollback.add_argument("--target", required=True)
    args = parser.parse_args()
    if args.command == "rollback":
        restore(args.snapshot, args.target)


if __name__ == "__main__":
    main()
