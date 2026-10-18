"""Evaluates one spec operation from text arguments and returns 'ok:<value>' or 'error:<code>'.

Run as `python -m testing_strategies_polyglot.evaluate`: reads tab-separated lines (operation,
arguments...) on stdin and prints one result line each. The Java and JavaScript versions use the
same protocol, so one harness can drive all three.
"""

from __future__ import annotations

import sys

from . import dates, money


def _int(text: str) -> int:
    """An integer argument; anything else is an invalid amount."""
    try:
        return int(text)
    except ValueError:
        raise money.SpecError("invalid_amount") from None


def run(op: str, args: list[str]) -> str:
    """One operation; never raises."""
    try:
        match op, args:
            case "parse", [text, cur]:
                return f"ok:{money.parse(text, cur)}"
            case "add", [a, b, cur]:
                return f"ok:{money.add(_int(a), _int(b), cur)}"
            case "subtract", [a, b, cur]:
                return f"ok:{money.subtract(_int(a), _int(b), cur)}"
            case "multiply", [a, cur, factor]:
                return f"ok:{money.multiply(_int(a), cur, factor)}"
            case "allocate", [a, cur, ratios]:
                parts = money.allocate(_int(a), cur, [_ratio(r) for r in ratios.split(",")])
                return "ok:" + ",".join(str(p) for p in parts)
            case "format", [a, cur]:
                return f"ok:{money.format_money(_int(a), cur)}"
            case "days", [s, e]:
                return f"ok:{dates.days(s, e)}"
            case "contains", [s, e, d]:
                return f"ok:{str(dates.contains(s, e, d)).lower()}"
            case "overlaps", [s1, e1, s2, e2]:
                return f"ok:{str(dates.overlaps(s1, e1, s2, e2)).lower()}"
            case "split", [s, e]:
                return "ok:" + ",".join(f"{a}/{b}" for a, b in dates.split_by_month(s, e))
            case "localdate", [instant, zone]:
                return f"ok:{dates.local_date(instant, zone)}"
        return "error:unknown_operation"
    except money.SpecError as e:
        return f"error:{e.code}"


def _ratio(text: str) -> int:
    """A ratio argument."""
    try:
        return int(text)
    except ValueError:
        raise money.SpecError("invalid_ratios") from None


def main() -> None:
    """Answer each stdin line."""
    for line in sys.stdin:
        parts = line.rstrip("\n").split("\t")
        print(run(parts[0], parts[1:]), flush=True)


if __name__ == "__main__":
    main()
