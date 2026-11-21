"""R4: Reject invalid input (negative or non-numeric durations) with a clear message."""

from datetime import date

import pytest

from study_logger.cli import main
from study_logger.validation import ValidationError, parse_course, parse_date, parse_minutes

TODAY = date(2026, 11, 20)


def run_log(tmp_path, capsys, *args):
    data = tmp_path / "sessions.jsonl"
    code = main(["--file", str(data), "log", *args], today=TODAY)
    out, err = capsys.readouterr()
    return code, out, err, data


@pytest.mark.parametrize("bad", ["abc", "", "12abc", "1,5", "nan", "inf", "-inf"])
def test_r4_non_numeric_duration_rejected(tmp_path, capsys, bad):
    """R4: a non-numeric duration is rejected with a clear message and nothing is saved."""
    code, out, err, data = run_log(tmp_path, capsys, "CS101", bad)

    assert code == 1
    assert err.strip() == f"Error: duration must be a number of minutes, got '{bad}'."
    assert out == ""
    assert not data.exists()


@pytest.mark.parametrize("bad", ["-5", "-0.5", "0", "0.0"])
def test_r4_negative_or_zero_duration_rejected(tmp_path, capsys, bad):
    """R4: a negative (or zero) duration is rejected with a clear message and nothing is saved."""
    code, out, err, data = run_log(tmp_path, capsys, "CS101", bad)

    assert code == 1
    assert err.strip() == f"Error: duration must be greater than 0 minutes, got '{bad}'."
    assert not data.exists()


@pytest.mark.parametrize("bad", ["", "   "])
def test_r4_empty_course_rejected(tmp_path, capsys, bad):
    """R4: an empty course name is rejected."""
    code, _, err, data = run_log(tmp_path, capsys, bad, "45")

    assert code == 1
    assert err.strip() == "Error: course name must not be empty."
    assert not data.exists()


@pytest.mark.parametrize("bad", ["2026-13-01", "20-11-2026", "yesterday", "2026-02-30"])
def test_r4_invalid_log_date_rejected(tmp_path, capsys, bad):
    """R4: a --date that is not a real YYYY-MM-DD date is rejected."""
    code, _, err, data = run_log(tmp_path, capsys, "CS101", "45", "--date", bad)

    assert code == 1
    assert err.strip() == f"Error: date must be in YYYY-MM-DD format, got '{bad}'."
    assert not data.exists()


def test_r4_invalid_report_week_rejected(tmp_path, capsys):
    """R4: a --week that is not a valid date is rejected."""
    code = main(["--file", str(tmp_path / "s.jsonl"), "report", "--week", "next"], today=TODAY)

    assert code == 1
    assert capsys.readouterr().err.strip() == (
        "Error: date must be in YYYY-MM-DD format, got 'next'."
    )


def test_r4_invalid_input_leaves_existing_data_untouched(tmp_path, capsys):
    """R4: a rejected log does not change an existing data file."""
    data = tmp_path / "sessions.jsonl"
    main(["--file", str(data), "log", "CS101", "45"], today=TODAY)
    before = data.read_bytes()

    main(["--file", str(data), "log", "CS101", "-10"], today=TODAY)

    assert data.read_bytes() == before


def test_r4_parse_minutes_accepts_valid_values():
    """R4: valid positive durations pass validation (surrounding spaces allowed)."""
    assert parse_minutes("45") == 45.0
    assert parse_minutes("37.5") == 37.5
    assert parse_minutes(" 10 ") == 10.0


def test_r4_validators_raise_validation_error():
    """R4: each validator raises ValidationError for bad input."""
    with pytest.raises(ValidationError):
        parse_minutes("-1")
    with pytest.raises(ValidationError):
        parse_course(" ")
    with pytest.raises(ValidationError):
        parse_date("2026/11/20")
