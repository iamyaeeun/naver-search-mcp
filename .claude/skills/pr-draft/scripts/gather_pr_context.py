#!/usr/bin/env python3
"""Gather raw context for a PR description: commit list, changed-file stat,
and naming-convention violations. Prints markdown; does not write files or
touch GitHub — Claude reads this output and drafts the actual PR body.

Usage:
    python3 gather_pr_context.py [base_ref]   # base_ref defaults to "main"
"""
import subprocess
import sys
from pathlib import Path


def run(cmd: list[str]) -> str:
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout.strip()


def main() -> int:
    base_ref = sys.argv[1] if len(sys.argv) > 1 else "main"
    range_spec = f"{base_ref}...HEAD"

    commits = run(["git", "log", range_spec, "--oneline"])
    stat = run(["git", "diff", range_spec, "--stat"])

    naming_script = Path(__file__).parent.parent.parent / "naming-check" / "scripts" / "check_naming.py"
    naming_report = run(["python3", str(naming_script), range_spec])

    print("## Commits\n")
    print(commits or "(no commits found — check base_ref)")
    print("\n## Changed files\n")
    print(stat or "(no diff found)")
    print("\n## Naming check\n")
    print(naming_report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
