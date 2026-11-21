"""R1: Record a study session with a course name and a duration from the terminal."""

import json
from datetime import date

from study_logger.cli import main

TODAY = date(2026, 11, 20)


def read_lines(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def test_r1_log_records_course_minutes_and_today(tmp_path, capsys):
    """R1: `log COURSE MINUTES` stores one session dated today."""
    data = tmp_path / "sessions.jsonl"

    code = main(["--file", str(data), "log", "CS101", "45"], today=TODAY)

    assert code == 0
    assert read_lines(data) == [{"course": "CS101", "minutes": 45.0, "date": "2026-11-20"}]


def test_r1_log_prints_confirmation(tmp_path, capsys):
    """R1: logging prints a confirmation naming minutes, course and date."""
    data = tmp_path / "sessions.jsonl"

    main(["--file", str(data), "log", "CS101", "45"], today=TODAY)

    assert capsys.readouterr().out.strip() == "Logged 45 min for CS101 on 2026-11-20."


def test_r1_log_accepts_decimal_minutes(tmp_path):
    """R1: decimal minutes such as 37.5 are accepted."""
    data = tmp_path / "sessions.jsonl"

    code = main(["--file", str(data), "log", "Calc II", "37.5"], today=TODAY)

    assert code == 0
    assert read_lines(data)[0]["minutes"] == 37.5


def test_r1_log_with_explicit_date(tmp_path):
    """R1: --date YYYY-MM-DD backdates a forgotten session."""
    data = tmp_path / "sessions.jsonl"

    main(["--file", str(data), "log", "History", "30", "--date", "2026-11-17"], today=TODAY)

    assert read_lines(data)[0]["date"] == "2026-11-17"


def test_r1_log_trims_course_name(tmp_path):
    """R1: surrounding whitespace in the course name is removed."""
    data = tmp_path / "sessions.jsonl"

    main(["--file", str(data), "log", "  CS101  ", "45"], today=TODAY)

    assert read_lines(data)[0]["course"] == "CS101"


def test_r1_each_log_appends_one_session(tmp_path):
    """R1: every log call adds exactly one session."""
    data = tmp_path / "sessions.jsonl"

    main(["--file", str(data), "log", "CS101", "45"], today=TODAY)
    main(["--file", str(data), "log", "History", "20"], today=TODAY)

    assert [s["course"] for s in read_lines(data)] == ["CS101", "History"]
