#!/usr/bin/env python3
"""Scan a git diff's *added* lines for function/variable naming-convention violations.

Scope is intentionally narrow: only newly added function and variable
declarations are checked (not the whole file), and only two rules are
enforced (case convention + non-descriptive names). This is meant as a
fast pre-PR sanity check, not a full linter.

Usage:
    python3 check_naming.py                # diff against working tree (unstaged changes)
    python3 check_naming.py --cached        # diff staged changes
    python3 check_naming.py main...HEAD     # diff against a base ref
"""
import re
import subprocess
import sys

PY_EXT = (".py",)
JS_EXT = (".js", ".jsx", ".ts", ".tsx")

# [^\W\d] = a "word" char that isn't a digit (unicode-aware, so this also
# captures non-ASCII identifiers like Korean names instead of silently
# skipping the line).
PY_IDENT = r"[^\W\d]\w*"
JS_IDENT = r"(?:[^\W\d]|\$)[\w$]*"

PY_DEF_RE = re.compile(rf"^\+\s*def\s+({PY_IDENT})\s*\(")
PY_ASSIGN_RE = re.compile(rf"^\+\s*({PY_IDENT})\s*=(?!=)")
JS_FUNC_RE = re.compile(rf"^\+\s*(?:export\s+)?function\s+({JS_IDENT})\s*\(")
JS_DECL_RE = re.compile(rf"^\+\s*(?:export\s+)?(?:const|let|var)\s+({JS_IDENT})\s*=")

ALLOWED_SHORT_NAMES = {"i", "j", "k", "x", "y", "n", "_"}


def run_git_diff(diff_args: list[str]) -> str:
    cmd = ["git", "diff", "-U0", *diff_args]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return result.stdout


def is_non_ascii(name: str) -> bool:
    return any(ord(ch) > 127 for ch in name)


def check_python_name(name: str) -> str | None:
    if is_non_ascii(name):
        return "non-ASCII identifier"
    if re.fullmatch(r"[A-Z_][A-Z0-9_]*", name):
        return None  # ALL_CAPS constants are fine
    if not re.fullmatch(r"[a-z_][a-z0-9_]*", name):
        return "not snake_case"
    if len(name) == 1 and name not in ALLOWED_SHORT_NAMES:
        return "single-letter, non-descriptive name"
    return None


def check_js_name(name: str) -> str | None:
    if is_non_ascii(name):
        return "non-ASCII identifier"
    # allow a leading underscore/$ (private-field convention), but no
    # underscores after that — camelCase, not snake_case.
    body = name.lstrip("_$")
    if not body or not re.fullmatch(r"[a-z][a-zA-Z0-9]*", body):
        return "not camelCase"
    if len(name) == 1 and name not in ALLOWED_SHORT_NAMES:
        return "single-letter, non-descriptive name"
    return None


def scan(diff_text: str) -> list[tuple[str, int, str, str]]:
    violations = []
    current_file = None
    lang = None
    line_no = 0

    for line in diff_text.splitlines():
        if line.startswith("+++ "):
            path = line[4:].strip()
            current_file = path[2:] if path.startswith("b/") else path
            if current_file.endswith(PY_EXT):
                lang = "py"
            elif current_file.endswith(JS_EXT):
                lang = "js"
            else:
                lang = None
            continue

        if line.startswith("@@"):
            m = re.search(r"\+(\d+)", line)
            line_no = int(m.group(1)) - 1 if m else 0
            continue

        if not line.startswith("+") or line.startswith("+++"):
            continue

        line_no += 1
        if lang is None or current_file is None:
            continue

        if lang == "py":
            for pattern in (PY_DEF_RE, PY_ASSIGN_RE):
                m = pattern.match(line)
                if m:
                    issue = check_python_name(m.group(1))
                    if issue:
                        violations.append((current_file, line_no, m.group(1), issue))
        else:
            for pattern in (JS_FUNC_RE, JS_DECL_RE):
                m = pattern.match(line)
                if m:
                    issue = check_js_name(m.group(1))
                    if issue:
                        violations.append((current_file, line_no, m.group(1), issue))

    return violations


def main() -> int:
    diff_args = sys.argv[1:]
    try:
        diff_text = run_git_diff(diff_args)
    except subprocess.CalledProcessError as e:
        print(f"git diff failed: {e.stderr}", file=sys.stderr)
        return 1

    violations = scan(diff_text)
    if not violations:
        print("✅ No naming issues found in the diff.")
        return 0

    print(f"⚠️  {len(violations)} naming issue(s) found:\n")
    for path, line_no, name, issue in violations:
        print(f"  {path}:{line_no}  `{name}`  — {issue}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
