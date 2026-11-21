"""Command-line interface: ``log`` (R1) and ``report`` (R3)."""

import argparse
import re
import sys
from datetime import date
from pathlib import Path

from .report import format_number, format_report
from .storage import Session, append_session, load_sessions
from .validation import ValidationError, parse_course, parse_date, parse_minutes

DEFAULT_FILE = "sessions.jsonl"


class _Parser(argparse.ArgumentParser):
    """ArgumentParser that passes values like ``-5`` or ``-inf`` through as arguments.

    By default argparse mistakes ``-inf``/``-nan`` for unknown options, which
    would hide our clear R4 error message behind a generic usage error.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._negative_number_matcher = re.compile(r"^-(\d|\.\d|inf|nan)", re.IGNORECASE)


def build_parser() -> argparse.ArgumentParser:
    parser = _Parser(
        prog="study_logger",
        description="Log study sessions per course and report weekly totals.",
    )
    parser.add_argument(
        "--file",
        default=DEFAULT_FILE,
        help=f"data file to use (default: {DEFAULT_FILE} in the current folder)",
    )
    commands = parser.add_subparsers(dest="command", required=True)

    log = commands.add_parser("log", help="record a study session")
    log.add_argument("course", help="course name, e.g. CS101 (quote names with spaces)")
    log.add_argument("minutes", help="session length in minutes, e.g. 45 or 37.5")
    log.add_argument("--date", help="session date as YYYY-MM-DD (default: today)")

    report = commands.add_parser("report", help="show total minutes per course for a week")
    report.add_argument("--week", help="any date YYYY-MM-DD in the week (default: this week)")

    return parser


def main(argv: list[str] | None = None, today: date | None = None) -> int:
    args = build_parser().parse_args(argv)
    today = today or date.today()
    path = Path(args.file)

    try:
        if args.command == "log":
            session = Session(
                course=parse_course(args.course),
                minutes=parse_minutes(args.minutes),
                day=parse_date(args.date) if args.date else today,
            )
            append_session(path, session)
            print(
                f"Logged {format_number(session.minutes)} min for {session.course} "
                f"on {session.day.isoformat()}."
            )
        else:
            day = parse_date(args.week) if args.week else today
            print(format_report(load_sessions(path), day))
    except ValidationError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0
