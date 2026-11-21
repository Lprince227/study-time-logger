# CLAUDE.md — standing rules for this repository

- **Language:** Python (standard library only for the program; `pytest` for tests).
- **Run tests:** `py -m pytest`
- **Requirement IDs in tests:** every test names the requirement it checks
  (e.g. `R2`) in its name and/or docstring, e.g. `test_r2_sessions_persist_between_runs`.
- **Spec first:** `spec.md` is the source of truth for behavior; update it
  when a requirement changes.
- **Commits:** small, focused commits. Each message says what changed and why.
- **Never undo or amend a commit** (no `git commit --amend`, `git reset`,
  `git rebase`, or force-push). Fix mistakes with a new commit.
- **Never commit** `.venv/` or any `*.jsonl` file (study-session data).
