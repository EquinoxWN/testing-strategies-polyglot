"""Date ranges with an excluded end date, and UTC instants to local dates in a time zone."""

from __future__ import annotations

import re
from datetime import UTC, date, datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from .money import SpecError

INSTANT = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
ZONE = re.compile(r"^[A-Za-z_]+(/[A-Za-z_+\-0-9]+)*$")


def parse_date(text: str) -> date:
    """A strict ISO date (YYYY-MM-DD)."""
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", text):
        raise SpecError("invalid_date")
    try:
        return date.fromisoformat(text)
    except ValueError:
        raise SpecError("invalid_date") from None


def parse_range(start: str, end: str) -> tuple[date, date]:
    """A range [start, end); start after end is an error."""
    s, e = parse_date(start), parse_date(end)
    if s > e:
        raise SpecError("invalid_range")
    return s, e


def days(start: str, end: str) -> int:
    """Number of days in [start, end)."""
    s, e = parse_range(start, end)
    return (e - s).days


def contains(start: str, end: str, day: str) -> bool:
    """Whether day is in [start, end)."""
    s, e = parse_range(start, end)
    d = parse_date(day)
    return s <= d < e


def overlaps(s1: str, e1: str, s2: str, e2: str) -> bool:
    """Whether two ranges share a day; empty ranges overlap nothing."""
    a, b = parse_range(s1, e1)
    c, d = parse_range(s2, e2)
    if a == b or c == d:
        return False
    return a < d and c < b


def split_by_month(start: str, end: str) -> list[tuple[date, date]]:
    """Pieces of [start, end), each inside one calendar month."""
    s, e = parse_range(start, end)
    pieces = []
    while s < e:
        first_of_next = date(s.year + 1, 1, 1) if s.month == 12 else date(s.year, s.month + 1, 1)
        piece_end = min(first_of_next, e)
        pieces.append((s, piece_end))
        s = piece_end
    return pieces


def local_date(instant: str, zone: str) -> date:
    """The calendar date of a UTC instant in an IANA time zone."""
    if not INSTANT.match(instant):
        raise SpecError("invalid_date")
    try:
        moment = datetime.strptime(instant, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)
    except ValueError:
        raise SpecError("invalid_date") from None
    if not ZONE.match(zone):
        raise SpecError("invalid_zone")
    try:
        tz = ZoneInfo(zone)
    except (ZoneInfoNotFoundError, ValueError):
        raise SpecError("invalid_zone") from None
    return moment.astimezone(tz).date()
