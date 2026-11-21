"""Weekly per-course report (R3)."""

from datetime import date, timedelta
from typing import Iterable

from .storage import Session


def week_bounds(day: date) -> tuple[date, date]:
    """Return the Monday and Sunday of the week containing ``day``."""
    monday = day - timedelta(days=day.weekday())
    return monday, monday + timedelta(days=6)


def weekly_totals(sessions: Iterable[Session], day: date) -> list[tuple[str, float]]:
    """Total minutes per course for the week containing ``day``.

    Courses are grouped case-insensitively and shown with the first spelling
    seen. Sorted by total (largest first), then by name.
    """
    start, end = week_bounds(day)
    names: dict[str, str] = {}
    totals: dict[str, float] = {}
    for s in sessions:
        if not start <= s.day <= end:
            continue
        name = s.course.strip()
        key = name.casefold()
        names.setdefault(key, name)
        totals[key] = totals.get(key, 0) + s.minutes
    return sorted(
        ((names[key], total) for key, total in totals.items()),
        key=lambda item: (-item[1], item[0].casefold()),
    )


def format_number(minutes: float) -> str:
    """Render a minute count without a trailing ``.0`` (``45``, ``37.5``)."""
    if float(minutes).is_integer():
        return str(int(minutes))
    return f"{minutes:.2f}".rstrip("0").rstrip(".")


def format_minutes(minutes: float) -> str:
    """Render minutes as e.g. ``90 min (1h 30m)``."""
    rounded = int(minutes + 0.5)
    hours, mins = divmod(rounded, 60)
    return f"{format_number(minutes)} min ({hours}h {mins:02d}m)"


def format_report(sessions: Iterable[Session], day: date) -> str:
    """Build the full report text for the week containing ``day``."""
    start, end = week_bounds(day)
    lines = [f"Week of {start.isoformat()} to {end.isoformat()}"]
    totals = weekly_totals(sessions, day)
    if not totals:
        lines.append("No study sessions recorded this week.")
    else:
        lines.extend(f"{course}: {format_minutes(total)}" for course, total in totals)
        lines.append(f"Total: {format_minutes(sum(t for _, t in totals))}")
    return "\n".join(lines)
