# 0001 — Store study sessions as JSON Lines

- Status: accepted
- Date: 2026-11-20
- Requirement: R2 (store sessions in a plain file that persists between runs)

## Y-statement

In the context of **persisting study sessions between runs of a small
single-user command-line tool (R2)**,
facing **the need for a plain, human-readable file that is safe to add to on
every `log` and easy to read back with the standard library**,
we decided for **JSON Lines (`sessions.jsonl`, one JSON object per line,
opened in append mode)**
and against **CSV, a single JSON array file, and SQLite**,
to achieve **append-only writes that never rewrite existing data, a corrupt
line that can be skipped on its own without losing the rest, and
unambiguous handling of course names containing commas or quotes**,
accepting **a file that is slightly more verbose than CSV, cannot be opened
directly as a spreadsheet, and needs a full scan for every report**.

## Alternatives considered

| Option | Why not chosen |
| --- | --- |
| **CSV** (`course,minutes,date`) | Also plain and append-friendly and opens in Excel, but course names with commas or quotes need correct quoting, and adding fields later changes column meaning. A close second. |
| **Single JSON array file** | Plain and readable, but every `log` must read, modify and rewrite the whole file; a crash mid-write or one bad character makes the whole file unreadable. |
| **SQLite** | Robust and queryable, but it is a binary file, not the "plain file" R2 asks for, and is more machinery than four requirements need. |

## Consequences

- `append_session` only ever appends one line; existing lines are never touched.
- `load_sessions` validates each line separately and skips bad ones with a
  warning naming the line number (see spec.md, R2).
- `*.jsonl` is git-ignored so personal study data is never committed.
- If reports become slow because the file grows very large, revisit SQLite.
