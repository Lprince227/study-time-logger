"""Plain-file storage of study sessions in JSON Lines format (R2)."""

import json
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from .validation import ValidationError, parse_course, parse_date, parse_minutes


@dataclass(frozen=True)
class Session:
    course: str
    minutes: float
    day: date


def append_session(path: Path, session: Session) -> None:
    """Append one session as a single JSON line, creating the file if needed."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    record = {
        "course": session.course,
        "minutes": float(session.minutes),
        "date": session.day.isoformat(),
    }
    with path.open("a", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(record) + "\n")


def load_sessions(path: Path) -> list[Session]:
    """Read all valid sessions from ``path``.

    A missing file means no sessions. Lines that are not valid sessions are
    skipped with a warning on stderr naming the line number.
    """
    path = Path(path)
    if not path.exists():
        return []

    sessions = []
    with path.open(encoding="utf-8") as f:
        for number, line in enumerate(f, start=1):
            if not line.strip():
                continue
            try:
                sessions.append(_parse_line(line))
            except (ValueError, KeyError, TypeError) as exc:
                print(f"Warning: skipping line {number} of {path}: {exc}", file=sys.stderr)
    return sessions


def _parse_line(line: str) -> Session:
    record = json.loads(line)
    if not isinstance(record, dict):
        raise ValidationError("not a JSON object.")
    course, minutes, day = record["course"], record["minutes"], record["date"]
    if not isinstance(course, str) or not isinstance(day, str):
        raise ValidationError("course and date must be text.")
    if isinstance(minutes, bool) or not isinstance(minutes, (int, float)):
        raise ValidationError("minutes must be a number.")
    return Session(parse_course(course), parse_minutes(str(minutes)), parse_date(day))
