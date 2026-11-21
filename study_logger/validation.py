"""Input validation for the study logger (R4)."""

import math
import re
from datetime import date


class ValidationError(ValueError):
    """Raised when user input is invalid; the message is shown to the user."""


_DATE_PATTERN = re.compile(r"\d{4}-\d{2}-\d{2}")


def parse_minutes(text: str) -> float:
    """Return a positive, finite number of minutes parsed from ``text``."""
    try:
        minutes = float(text)
    except ValueError:
        minutes = math.nan
    if not math.isfinite(minutes):
        raise ValidationError(f"duration must be a number of minutes, got '{text}'.")
    if minutes <= 0:
        raise ValidationError(f"duration must be greater than 0 minutes, got '{text}'.")
    return minutes


def parse_course(text: str) -> str:
    """Return the course name with surrounding whitespace removed."""
    course = text.strip()
    if not course:
        raise ValidationError("course name must not be empty.")
    return course


def parse_date(text: str) -> date:
    """Return the date for a strict ``YYYY-MM-DD`` string."""
    if _DATE_PATTERN.fullmatch(text):
        try:
            return date.fromisoformat(text)
        except ValueError:
            pass
    raise ValidationError(f"date must be in YYYY-MM-DD format, got '{text}'.")
