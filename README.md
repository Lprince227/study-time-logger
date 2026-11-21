# Study Time Logger

A small command-line tool for college students taking several courses. You log
each study session (course + minutes) from the terminal, and at any time you
can print how many minutes you spent on each course in a given week. That makes
it obvious which classes you are neglecting before deadlines arrive.

Sessions are saved in a plain text file (`sessions.jsonl`, one JSON object per
line) so they persist between runs. Invalid input such as negative or
non-numeric durations is rejected with a clear error message.

See [spec.md](spec.md) for the full behavior.

## Requirements

- Python 3.10 or newer (the `py` launcher on Windows)
- No third-party packages are needed to run the program; `pytest` is needed
  only for the tests.

## Running it

From the project folder:

```
py -m study_logger log CS101 45
py -m study_logger log "Calc II" 37.5 --date 2026-11-17
py -m study_logger report
py -m study_logger report --week 2026-11-10
```

- `log COURSE MINUTES [--date YYYY-MM-DD]` records a session (default date: today).
- `report [--week YYYY-MM-DD]` shows totals per course for the Monday–Sunday
  week containing that date (default: this week).
- `--file PATH` (placed before `log`/`report`) uses a different data file
  instead of `sessions.jsonl` in the current folder.

Example report:

```
Week of 2026-11-16 to 2026-11-22
CS101: 90 min (1h 30m)
History: 30 min (0h 30m)
Total: 120 min (2h 00m)
```

## Setting up a virtual environment and test requirements

Windows (PowerShell):

```
py -m venv .venv
.venv\Scripts\Activate.ps1
py -m pip install -r requirements-dev.txt
```

macOS / Linux:

```
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
```

## Running the tests

```
py -m pytest
```

Every test names the requirement (R1–R4) it checks.
