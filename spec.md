# Study Time Logger — Specification (round 2)

A command-line tool for college students to log how long they study each
course and see a weekly total per course, so neglected courses become visible
before deadlines arrive.

## Commands

The program runs as a Python module:

```
py -m study_logger [--file PATH] log COURSE MINUTES [--date YYYY-MM-DD]
py -m study_logger [--file PATH] report [--week YYYY-MM-DD]
```

`--file PATH` selects the data file. Default: `sessions.jsonl` in the current
working directory.

Exit codes: `0` on success, `1` on invalid input, `2` on command-line usage
errors (unknown command, missing argument — produced by `argparse`).

## R1 — Record a study session

`log COURSE MINUTES` records one session.

- `COURSE` is any non-empty text. Leading and trailing whitespace is removed
  before saving. Quote names containing spaces (`"Calc II"`).
- `MINUTES` is the session length in minutes. Whole numbers and decimals are
  accepted (`45`, `37.5`).
- The session is dated today (local date) unless `--date YYYY-MM-DD` is given,
  which allows logging a session that was forgotten.
- On success the program prints a confirmation, e.g.
  `Logged 45 min for CS101 on 2026-11-20.`

## R2 — Persist sessions in a plain file

- Sessions are stored in a plain text file in JSON Lines format: one JSON
  object per line, appended on each `log`:

  ```
  {"course": "CS101", "minutes": 45.0, "date": "2026-11-20"}
  ```

- The file is created on first `log` if it does not exist. Existing lines are
  never rewritten.
- Sessions logged in one run are visible to `report` in any later run.
- If the file does not exist, `report` treats it as having no sessions.
- A line that is not a valid session (bad JSON, missing fields, bad values) is
  skipped and a warning naming the line number is printed to stderr; the
  remaining sessions are still reported.

## R3 — Weekly report per course

`report` prints the total minutes per course for one week.

- A week runs Monday through Sunday.
- `--week YYYY-MM-DD` selects the week containing that date. Without it, the
  current week (containing today) is reported.
- Course names are grouped case-insensitively after trimming whitespace
  (`cs101`, `CS101` and ` CS101 ` are one course). The report shows the
  spelling used in the earliest stored session for that course.
- Only sessions whose date falls within the week are counted.
- Courses are listed by total time, largest first; ties are ordered by name.
- Output format:

  ```
  Week of 2026-11-16 to 2026-11-22
  CS101: 90 min (1h 30m)
  History: 30 min (0h 30m)
  Total: 120 min (2h 00m)
  ```

- If the week has no sessions, it prints the week header followed by
  `No study sessions recorded this week.`
- The report always ends with the "Not Studied" section described in R5.

## R5 — "Not Studied" section for neglected courses

*Added in round 2.* The weekly report ends with a section titled
`Not Studied`. It lists courses that were studied before this week but have
no sessions this week.

- A course is **not studied** when it has at least one session dated before
  the Monday of the reported week and no session inside the reported week.
  Every earlier week counts, not only the previous one. Sessions dated after
  the reported week are ignored, so a report for a past week only looks at
  history from before that week.
- Courses are matched the same way as in R3: case-insensitively after
  trimming whitespace. A course studied this week under any spelling is not
  listed.
- Each course is shown with zero minutes in the R3 line format
  (`History: 0 min (0h 00m)`). The name uses the spelling of the earliest
  stored session for that course.
- Courses are listed alphabetically (case-insensitive).
- The section comes after the `Total:` line (or after
  `No study sessions recorded this week.`). A blank line separates it from the
  lines above it. Not-studied courses do not change the `Total:` line.
- The heading is always printed. If no course qualifies, one line comes after
  it:
  - `None - every course was studied this week.` when earlier courses exist
    and all of them were studied this week;
  - `None - no courses were logged in earlier weeks.` when no session is dated
    before the reported week.

Example (Biology and History were studied in earlier weeks but not this
week):

```
Week of 2026-11-16 to 2026-11-22
CS101: 90 min (1h 30m)
Total: 90 min (1h 30m)

Not Studied
Biology: 0 min (0h 00m)
History: 0 min (0h 00m)
```

Example (a week with no sessions):

```
Week of 2026-11-23 to 2026-11-29
No study sessions recorded this week.

Not Studied
CS101: 0 min (0h 00m)
History: 0 min (0h 00m)
```

## R4 — Reject invalid input

Invalid input is rejected with a clear message on stderr, exit code `1`, and
nothing is written to the data file.

| Input | Rejected because | Message (example) |
| --- | --- | --- |
| `MINUTES` not a number (`abc`, `""`) | non-numeric | `Error: duration must be a number of minutes, got 'abc'.` |
| `MINUTES` negative (`-5`) | negative | `Error: duration must be greater than 0 minutes, got '-5'.` |
| `MINUTES` is `0` | zero tells nothing | `Error: duration must be greater than 0 minutes, got '0'.` |
| `MINUTES` is `nan` / `inf` | not a real duration | `Error: duration must be a number of minutes, got 'inf'.` |
| `COURSE` empty or only spaces | no course | `Error: course name must not be empty.` |
| `--date` / `--week` not a valid `YYYY-MM-DD` date | bad date | `Error: date must be in YYYY-MM-DD format, got '2026-13-01'.` |

## Out of scope (rounds 1 and 2)

Editing or deleting sessions, start/stop timers, multiple users, reports over
ranges other than a single week.
