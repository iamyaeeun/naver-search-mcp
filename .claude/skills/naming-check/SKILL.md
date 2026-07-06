---
name: naming-check
description: Check newly added function/variable names in the current git diff against this repo's naming convention (snake_case for Python, camelCase for JS/TS, no non-descriptive single-letter or non-ASCII names). Use before opening a PR, or whenever the user asks to check naming/코드 컨벤션/변수명.
---

# Naming Convention Check

Scope is deliberately narrow: this only looks at **added lines** in the current
diff, and only at function/variable declarations. It does not run a full
linter and does not touch unchanged code.

## When to use

- Right before drafting or opening a PR.
- When the user asks to check naming, variable names, or code convention on
  their current changes.

## How to run

```bash
python3 .claude/skills/naming-check/scripts/check_naming.py [git-diff-args]
```

- No args: diffs unstaged working-tree changes.
- `--cached`: diffs staged changes.
- `<base>...HEAD`: diffs against a base branch/ref (use this before opening a PR).

The script exits non-zero and prints a list of `file:line — issue` when it
finds violations, or a single ✅ line when clean.

## Rules enforced

1. Python function/variable names must be `snake_case` (ALL_CAPS constants
   are allowed).
2. JS/TS function/variable names must be `camelCase`.
3. No non-ASCII (e.g. Korean) identifiers.
4. No single-letter names except common loop/index conventions (`i, j, k, x,
   y, n, _`).

## Reporting back

When invoked as part of a PR workflow, include the script's output verbatim
in the PR description under a "Naming check" section rather than
paraphrasing it.
