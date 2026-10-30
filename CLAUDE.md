# CLAUDE.md

## Workflow

- Never commit to `master`. It's protected, and only PRs can change it. Always create a short-lived branch (`<type>/<desc>`) and open a PR.
- PRs are squash-merged, so the **PR title becomes the commit message on `master`**. Use a conventional prefix: `feat:`, `fix:`, `chore:`, `ci:`, `style:`, `docs:`, `data:` (new polls), `chore(deps):`.
- `ci-ok` is the only required check. It passes when lint (ruff) and tests (pytest, Python 3.11–3.14) pass. The branch must be up to date with `master`.
- Loop: `git switch -c <type>/<desc>` → commit → `gh pr create --fill` → `gh pr merge --auto --squash` → `git switch master && git pull`.

## Notes

- Monte Carlo simulator for Israeli election polls, allocating seats with the Bader-Ofer method.
- Poll JSON `results` are fractions, not percentages.
- The Pages deploy runs on pushes to `master` touching `output/26th-Knesset-2026/**`. The election is set only in `.github/workflows/pages.yml`.
