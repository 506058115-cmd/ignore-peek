#!/usr/bin/env python3
"""Check Git ignore status without changing the repository."""

import argparse
import json
from pathlib import Path
import subprocess
import sys


MAX_PATHS = 100
MAX_PATH_LENGTH = 4_096


def main():
    parser = argparse.ArgumentParser(description="Check whether paths match Git ignore rules; do not modify files.")
    parser.add_argument("paths", nargs="+", help="repository-relative paths to inspect")
    parser.add_argument("--repo", type=Path, default=Path("."), help="repository directory (default: current directory)")
    args = parser.parse_args()
    if len(args.paths) > MAX_PATHS:
        parser.error(f"at most {MAX_PATHS} paths are allowed")
    if any("\0" in path or len(path) > MAX_PATH_LENGTH for path in args.paths):
        parser.error(f"paths must be shorter than {MAX_PATH_LENGTH + 1} characters and contain no NUL")
    if "\0" in str(args.repo):
        parser.error("repository path cannot contain NUL")

    ignored = 0
    try:
        repository = subprocess.run(
            ["git", "-C", str(args.repo), "rev-parse", "--is-inside-work-tree"],
            stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
            text=True, check=False,
        )
        if repository.returncode or repository.stdout.strip() != "true":
            print("ignore-peek: repository is not a Git work tree", file=sys.stderr)
            return 2
        for path in args.paths:
            result = subprocess.run(
                ["git", "-C", str(args.repo), "check-ignore", "--no-index", "--quiet", "--", path],
                stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                check=False,
            )
            if result.returncode == 0:
                status = "ignored"
                ignored += 1
            elif result.returncode == 1:
                status = "not ignored"
            else:
                print(f"ignore-peek: Git could not inspect {json.dumps(path, ensure_ascii=True)}", file=sys.stderr)
                return 2
            print(f"{json.dumps(path, ensure_ascii=True)}: {status}")
    except OSError:
        print("ignore-peek: Git could not be started", file=sys.stderr)
        return 2

    print(f"Ignored: {ignored}; not ignored: {len(args.paths) - ignored}.")
    return 0 if ignored == len(args.paths) else 1


if __name__ == "__main__":
    raise SystemExit(main())
