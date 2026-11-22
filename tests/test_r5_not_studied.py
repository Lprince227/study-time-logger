"""R5: Weekly report includes a "Not Studied" section listing courses logged in
an earlier week that have no sessions this week, shown with zero minutes."""

from datetime import date

from study_logger.cli import main
from study_logger.report import not_studied
from study_logger.storage import Session

TODAY = date(2026, 11, 20)  # a Friday; its week is Mon 2026-11-16 .. Sun 2026-11-22
WEEK = date(2026, 11, 18)


def log(data, course, minutes, day):
    assert main(["--file", str(data), "log", course, str(minutes), "--date", day], today=TODAY) == 0


def report(data, capsys, *args):
    capsys.readouterr()  # discard output from earlier log calls
    code = main(["--file", str(data), "report", *args], today=TODAY)
    return code, capsys.readouterr().out.splitlines()


def test_r5_lists_course_from_earlier_week_missing_this_week():
    """R5: a course logged in an earlier week but not this week is not studied."""
    sessions = [
        Session("CS101", 45, date(2026, 11, 17)),
        Session("History", 30, date(2026, 11, 10)),
    ]

    assert not_studied(sessions, WEEK) == ["History"]


def test_r5_any_earlier_week_counts_not_only_previous():
    """R5: a course last studied several weeks ago is still listed."""
    sessions = [Session("Biology", 30, date(2026, 9, 1))]

    assert not_studied(sessions, WEEK) == ["Biology"]


def test_r5_course_studied_this_week_is_not_listed():
    """R5: a course with sessions both earlier and this week is not listed."""
    sessions = [
        Session("CS101", 45, date(2026, 11, 9)),
        Session("CS101", 45, date(2026, 11, 22)),  # Sunday, last day of the week
    ]

    assert not_studied(sessions, WEEK) == []


def test_r5_later_weeks_are_ignored():
    """R5: sessions dated after the reported week do not make a course 'not studied'."""
    sessions = [Session("History", 30, date(2026, 11, 23))]  # next Monday

    assert not_studied(sessions, WEEK) == []


def test_r5_previous_sunday_counts_as_earlier_week():
    """R5: the day before the reported Monday belongs to an earlier week."""
    sessions = [Session("History", 30, date(2026, 11, 15))]

    assert not_studied(sessions, WEEK) == ["History"]


def test_r5_matches_courses_case_insensitively():
    """R5: 'cs101' this week counts as studying 'CS101' from an earlier week."""
    sessions = [
        Session("CS101", 45, date(2026, 11, 9)),
        Session(" cs101 ", 20, date(2026, 11, 17)),
    ]

    assert not_studied(sessions, WEEK) == []


def test_r5_uses_earliest_spelling_and_lists_each_course_once():
    """R5: a course is listed once, with the spelling of its earliest stored session."""
    sessions = [
        Session("History", 30, date(2026, 11, 2)),
        Session("history", 30, date(2026, 11, 9)),
    ]

    assert not_studied(sessions, WEEK) == ["History"]


def test_r5_sorted_alphabetically_case_insensitive():
    """R5: not-studied courses are listed A-Z, ignoring case."""
    sessions = [
        Session("history", 30, date(2026, 11, 9)),
        Session("Calc II", 30, date(2026, 11, 9)),
        Session("Biology", 30, date(2026, 11, 9)),
    ]

    assert not_studied(sessions, WEEK) == ["Biology", "Calc II", "history"]


def test_r5_report_shows_section_after_total(tmp_path, capsys):
    """R5: the section follows Total after a blank line, with zero-minute lines."""
    data = tmp_path / "sessions.jsonl"
    log(data, "History", 30, "2026-11-09")
    log(data, "Biology", 20, "2026-10-05")
    log(data, "CS101", 60, "2026-11-10")
    log(data, "CS101", 90, "2026-11-17")

    code, lines = report(data, capsys, "--week", "2026-11-18")

    assert code == 0
    assert lines == [
        "Week of 2026-11-16 to 2026-11-22",
        "CS101: 90 min (1h 30m)",
        "Total: 90 min (1h 30m)",
        "",
        "Not Studied",
        "Biology: 0 min (0h 00m)",
        "History: 0 min (0h 00m)",
    ]


def test_r5_empty_week_shows_no_sessions_line_and_section(tmp_path, capsys):
    """R5: a week with no sessions keeps the R3 message and lists every earlier course."""
    data = tmp_path / "sessions.jsonl"
    log(data, "CS101", 45, "2026-11-17")
    log(data, "History", 30, "2026-11-10")

    code, lines = report(data, capsys, "--week", "2026-11-25")

    assert code == 0
    assert lines == [
        "Week of 2026-11-23 to 2026-11-29",
        "No study sessions recorded this week.",
        "",
        "Not Studied",
        "CS101: 0 min (0h 00m)",
        "History: 0 min (0h 00m)",
    ]


def test_r5_heading_with_none_when_every_course_studied(tmp_path, capsys):
    """R5: if all earlier courses were studied this week, the heading is followed by 'None'."""
    data = tmp_path / "sessions.jsonl"
    log(data, "CS101", 45, "2026-11-09")
    log(data, "CS101", 45, "2026-11-17")

    code, lines = report(data, capsys, "--week", "2026-11-18")

    assert code == 0
    assert lines[-3:] == ["", "Not Studied", "None - every course was studied this week."]


def test_r5_heading_with_none_when_no_earlier_history(tmp_path, capsys):
    """R5: with no sessions before the week, the section says there is no earlier history."""
    data = tmp_path / "sessions.jsonl"
    log(data, "CS101", 45, "2026-11-17")
    log(data, "History", 30, "2026-11-30")  # a later week, ignored

    code, lines = report(data, capsys, "--week", "2026-11-18")

    assert code == 0
    assert lines[-3:] == ["", "Not Studied", "None - no courses were logged in earlier weeks."]


def test_r5_section_shown_when_data_file_missing(tmp_path, capsys):
    """R5: even with no data file the report ends with the Not Studied section."""
    code, lines = report(tmp_path / "missing.jsonl", capsys)

    assert code == 0
    assert lines[-2:] == ["Not Studied", "None - no courses were logged in earlier weeks."]


def test_r5_not_studied_courses_do_not_change_total(tmp_path, capsys):
    """R5: zero-minute courses add nothing to the weekly Total line."""
    data = tmp_path / "sessions.jsonl"
    log(data, "History", 300, "2026-11-09")
    log(data, "CS101", 45, "2026-11-17")

    code, lines = report(data, capsys, "--week", "2026-11-18")

    assert code == 0
    assert "Total: 45 min (0h 45m)" in lines
