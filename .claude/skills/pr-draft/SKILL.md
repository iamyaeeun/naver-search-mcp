---
name: pr-draft
description: Draft a PR description from the current branch's diff against a base branch, including a naming-convention report, and optionally open it with `gh pr create`. Use when the user asks to open/draft a PR, write a PR description, or "PR 만들어줘"/"PR 초안".
---

# PR Draft

Turns the current branch's diff into a PR description, then opens the PR
only after the user confirms. Never push or open a PR silently.

## Steps

1. Confirm the base branch (default `main`) and that the working tree has
   no uncommitted changes you're about to lose — check with `git status`.
2. Run the context-gathering script:
   ```bash
   python3 .claude/skills/pr-draft/scripts/gather_pr_context.py <base_ref>
   ```
   This returns the commit list, changed-file stat, and a naming-check
   report (see [[naming-check]]) — all raw data, no prose.
3. Using that data plus your own reading of the diff (`git diff <base>...HEAD`),
   write the PR body from `templates/pr_template.md`:
   - **Summary**: 2-4 bullets on *why*, not a restatement of the diff stat.
   - **Naming check**: paste the script's output verbatim.
   - **Test plan**: concrete commands/steps the reviewer can run.
4. Show the drafted body to the user and ask for confirmation before doing
   anything that touches GitHub.
5. Only after explicit confirmation, run:
   ```bash
   gh pr create --title "<title>" --body-file <path-to-drafted-body>
   ```

## Rules

- Never run `gh pr create` (or `git push`) without the user explicitly
  approving the drafted body first.
- If naming-check reports violations, surface them in the draft rather than
  silently fixing or omitting them — let the user decide.
