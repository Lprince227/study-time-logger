"""R2: Store sessions in a plain file that persists between runs."""

import json
import subprocess
import sys
from datetime import date
from pathlib import Path

from study_logger.cli import main
from study_logger.storage import Session, append_session, load_sessions

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def test_r2_file_is_plain_json_lines(tmp_path):
    """R2: the data file is plain text, one JSON object per line."""
    data = tmp_path / "sessions.jsonl"
    append_session(data, Session("CS101", 45.0, date(2026, 11, 20)))
    append_session(data, Session("History", 30.0, date(2026, 11, 19)))

    lines = data.read_text(encoding="utf-8").splitlines()

    assert len(lines) == 2
    assert json.loads(lines[0]) == {"course": "CS101", "minutes": 45.0, "date": "2026-11-20"}


def test_r2_load_returns_what_was_appended(tmp_path):
    """R2: sessions read back equal the sessions written."""
    data = tmp_path / "sessions.jsonl"
    sessions = [
        Session("CS101", 45.0, date(2026, 11, 20)),
        Session("History", 30.5, date(2026, 11, 19)),
    ]
    for s in sessions:
        append_session(data, s)

    assert load_sessions(data) == sessions


def test_r2_missing_file_means_no_sessions(tmp_path):
    """R2: a data file that does not exist yet holds no sessions."""
    assert load_sessions(tmp_path / "nothing-here.jsonl") == []


def test_r2_log_creates_file_and_parent_dirs(tmp_path):
    """R2: the first log creates the data file (and its folder)."""
    data = tmp_path / "sub" / "sessions.jsonl"

    main(["--file", str(data), "log", "CS101", "45"], today=date(2026, 11, 20))

    assert data.exists()


def test_r2_appending_keeps_existing_lines(tmp_path):
    """R2: logging appends; earlier lines are left untouched."""
    data = tmp_path / "sessions.jsonl"
    data.write_text('{"course": "Old", "minutes": 10.0, "date": "2026-01-05"}\n', encoding="utf-8")

    main(["--file", str(data), "log", "CS101", "45"], today=date(2026, 11, 20))

    lines = data.read_text(encoding="utf-8").splitlines()
    assert lines[0] == '{"course": "Old", "minutes": 10.0, "date": "2026-01-05"}'
    assert len(lines) == 2


def test_r2_sessions_persist_between_separate_runs(tmp_path):
    """R2: a session logged by one process is reported by a later process."""
    data = tmp_path / "sessions.jsonl"

    def run(*args):
        return subprocess.run(
            [sys.executable, "-m", "study_logger", "--file", str(data), *args],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
        )

    first = run("log", "CS101", "45", "--date", "2026-11-18")
    assert first.returncode == 0, first.stderr

    second = run("report", "--week", "2026-11-18")
    assert second.returncode == 0, second.stderr
    assert "CS101: 45 min (0h 45m)" in second.stdout


def test_r2_malformed_line_is_skipped_with_warning(tmp_path, capsys):
    """R2: a corrupt line is skipped with a warning naming its line number."""
    data = tmp_path / "sessions.jsonl"
    data.write_text(
        '{"course": "CS101", "minutes": 45.0, "date": "2026-11-18"}\n'
        "this is not json\n"
        '{"course": "History", "minutes": 30.0, "date": "2026-11-18"}\n',
        encoding="utf-8",
    )

    sessions = load_sessions(data)

    assert [s.course for s in sessions] == ["CS101", "History"]
    assert "line 2" in capsys.readouterr().err


def test_r2_line_with_invalid_values_is_skipped(tmp_path, capsys):
    """R2: a line with a bad duration or date is skipped, not trusted."""
    data = tmp_path / "sessions.jsonl"
    data.write_text(
        '{"course": "CS101", "minutes": -5, "date": "2026-11-18"}\n'
        '{"course": "CS101", "minutes": 5, "date": "not-a-date"}\n'
        '{"course": "CS101"}\n',
        encoding="utf-8",
    )

    assert load_sessions(data) == []
    err = capsys.readouterr().err
    assert "line 1" in err and "line 2" in err and "line 3" in err
