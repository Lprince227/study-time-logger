"""R3: Report total time per course for a given week."""

from datetime import date

from study_logger.cli import main
from study_logger.report import format_minutes, week_bounds, weekly_totals
from study_logger.storage import Session

TODAY = date(2026, 11, 20)  # a Friday; its week is Mon 2026-11-16 .. Sun 2026-11-22


def log(data, course, minutes, day):
    assert main(["--file", str(data), "log", course, str(minutes), "--date", day], today=TODAY) == 0


def report(data, capsys, *args):
    capsys.readouterr()  # discard output from earlier log calls
    code = main(["--file", str(data), "report", *args], today=TODAY)
    return code, capsys.readouterr().out.splitlines()


def test_r3_week_runs_monday_to_sunday():
    """R3: the week containing any date runs from its Monday to its Sunday."""
    assert week_bounds(date(2026, 11, 20)) == (date(2026, 11, 16), date(2026, 11, 22))
    assert week_bounds(date(2026, 11, 16)) == (date(2026, 11, 16), date(2026, 11, 22))
    assert week_bounds(date(2026, 11, 22)) == (date(2026, 11, 16), date(2026, 11, 22))


def test_r3_week_can_span_month_and_year():
    """R3: week bounds work across month and year boundaries."""
    assert week_bounds(date(2027, 1, 1)) == (date(2026, 12, 28), date(2027, 1, 3))


def test_r3_totals_per_course_only_within_week():
    """R3: totals sum each course and ignore sessions outside the week."""
    sessions = [
        Session("CS101", 45, date(2026, 11, 16)),
        Session("CS101", 45, date(2026, 11, 22)),
        Session("History", 30, date(2026, 11, 18)),
        Session("CS101", 999, date(2026, 11, 15)),  # previous Sunday
        Session("History", 999, date(2026, 11, 23)),  # next Monday
    ]

    assert weekly_totals(sessions, date(2026, 11, 18)) == [("CS101", 90), ("History", 30)]


def test_r3_course_names_grouped_case_insensitively():
    """R3: 'CS101', 'cs101' and ' Cs101 ' count as one course, shown with first spelling."""
    sessions = [
        Session("CS101", 10, date(2026, 11, 16)),
        Session("cs101", 20, date(2026, 11, 17)),
        Session(" Cs101 ", 30, date(2026, 11, 18)),
    ]

    assert weekly_totals(sessions, date(2026, 11, 18)) == [("CS101", 60)]


def test_r3_sorted_by_total_descending_then_name():
    """R3: largest total first; ties ordered by course name."""
    sessions = [
        Session("Biology", 20, date(2026, 11, 16)),
        Session("Art", 20, date(2026, 11, 16)),
        Session("Chemistry", 50, date(2026, 11, 16)),
    ]

    assert [c for c, _ in weekly_totals(sessions, date(2026, 11, 16))] == [
        "Chemistry",
        "Art",
        "Biology",
    ]


def test_r3_format_minutes():
    """R3: minutes are shown with an hours-and-minutes form."""
    assert format_minutes(90) == "90 min (1h 30m)"
    assert format_minutes(45) == "45 min (0h 45m)"
    assert format_minutes(37.5) == "37.5 min (0h 38m)"
    assert format_minutes(120) == "120 min (2h 00m)"


def test_r3_report_command_output(tmp_path, capsys):
    """R3: `report --week DATE` prints header, one line per course, and a total."""
    data = tmp_path / "sessions.jsonl"
    log(data, "CS101", 45, "2026-11-16")
    log(data, "cs101", 45, "2026-11-19")
    log(data, "History", 30, "2026-11-18")

    code, lines = report(data, capsys, "--week", "2026-11-18")

    assert code == 0
    assert lines[:4] == [  # R5's Not Studied section follows; see test_r5_*
        "Week of 2026-11-16 to 2026-11-22",
        "CS101: 90 min (1h 30m)",
        "History: 30 min (0h 30m)",
        "Total: 120 min (2h 00m)",
    ]


def test_r3_report_defaults_to_current_week(tmp_path, capsys):
    """R3: without --week, the week containing today is reported."""
    data = tmp_path / "sessions.jsonl"
    log(data, "CS101", 45, "2026-11-20")
    log(data, "History", 30, "2026-11-09")  # two weeks earlier

    code, lines = report(data, capsys)

    assert code == 0
    assert lines[0] == "Week of 2026-11-16 to 2026-11-22"
    assert "CS101: 45 min (0h 45m)" in lines
    assert not any(line.startswith("History") for line in lines)


def test_r3_report_empty_week(tmp_path, capsys):
    """R3: a week without sessions says so instead of printing nothing."""
    data = tmp_path / "sessions.jsonl"
    log(data, "CS101", 45, "2026-11-20")

    code, lines = report(data, capsys, "--week", "2026-10-01")

    assert code == 0
    assert lines[:2] == [  # R5's Not Studied section follows; see test_r5_*
        "Week of 2026-09-28 to 2026-10-04",
        "No study sessions recorded this week.",
    ]


def test_r3_report_with_no_data_file(tmp_path, capsys):
    """R3: reporting before anything was logged works and shows an empty week."""
    code, lines = report(tmp_path / "missing.jsonl", capsys)

    assert code == 0
    assert lines[1] == "No study sessions recorded this week."
