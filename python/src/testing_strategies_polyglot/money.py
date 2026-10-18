"""Money in integer minor units: parse, add, subtract, multiply (half-even), allocate, format."""

from __future__ import annotations

import re

SCALES = {"USD": 2, "EUR": 2, "JPY": 0, "BHD": 3}
MAX_MINOR = 9_007_199_254_740_991  # 2**53 - 1: the same limit in Java, Python and JavaScript
FACTOR = re.compile(r"^-?\d{1,9}(\.\d{1,9})?$")


class SpecError(ValueError):
    """A spec error; code is the identifier shared by all three implementations."""

    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def scale(currency: str) -> int:
    """Decimal places of a currency."""
    if currency not in SCALES:
        raise SpecError("unknown_currency")
    return SCALES[currency]


def checked(minor: int) -> int:
    """The amount, or an overflow error outside +/- MAX_MINOR."""
    if abs(minor) > MAX_MINOR:
        raise SpecError("overflow")
    return minor


def parse(text: str, currency: str) -> int:
    """Parse a plain decimal like -12.34 into minor units; more decimals than the currency has is an error."""
    digits = scale(currency)
    pattern = rf"^-?\d{{1,16}}(\.\d{{1,{digits}}})?$" if digits else r"^-?\d{1,16}$"
    if not re.match(pattern, text):
        raise SpecError("invalid_amount")
    negative = text.startswith("-")
    whole, _, frac = text.lstrip("-").partition(".")
    minor = int(whole) * 10**digits + int(frac.ljust(digits, "0") or "0")
    return checked(-minor if negative else minor)


def add(a: int, b: int, currency: str) -> int:
    """a + b in one currency."""
    scale(currency)
    return checked(a + b)


def subtract(a: int, b: int, currency: str) -> int:
    """a - b in one currency."""
    scale(currency)
    return checked(a - b)


def round_half_even(numerator: int, denominator: int) -> int:
    """numerator / denominator rounded to the nearest integer, ties to even (banker's rounding)."""
    q, r = divmod(numerator, denominator)  # floor division: 0 <= r < denominator
    twice = 2 * r
    if twice > denominator or (twice == denominator and q % 2 == 1):
        q += 1
    return q


def multiply(minor: int, currency: str, factor: str) -> int:
    """minor x factor (a decimal string), rounded half-even to whole minor units."""
    scale(currency)
    if not FACTOR.match(factor):
        raise SpecError("invalid_factor")
    whole, _, frac = factor.partition(".")
    denominator = 10 ** len(frac)
    numerator = int(whole + frac)
    return checked(round_half_even(minor * numerator, denominator))


def allocate(minor: int, currency: str, ratios: list[int]) -> list[int]:
    """Split an amount by ratios without losing a minor unit; leftovers go to the first eligible parts."""
    scale(currency)
    if not 1 <= len(ratios) <= 100 or any(r < 0 for r in ratios) or sum(ratios) == 0:
        raise SpecError("invalid_ratios")
    total = sum(ratios)
    magnitude = abs(minor)
    parts = [magnitude * r // total for r in ratios]
    leftover = magnitude - sum(parts)
    for i, r in enumerate(ratios):
        if leftover == 0:
            break
        if r > 0:
            parts[i] += 1
            leftover -= 1
    return [-p if minor < 0 else p for p in parts]


def format_money(minor: int, currency: str) -> str:
    """Like '-12.34 USD'; JPY has no decimals, BHD three."""
    digits = scale(currency)
    sign = "-" if minor < 0 else ""
    whole, frac = divmod(abs(minor), 10**digits)
    body = f"{whole}.{frac:0{digits}d}" if digits else str(whole)
    return f"{sign}{body} {currency}"
