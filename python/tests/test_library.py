"""A few direct checks of the library API next to the spec rows."""

from __future__ import annotations

import pytest

from testing_strategies_polyglot import dates, money
from testing_strategies_polyglot.evaluate import run


def test_round_half_even_on_both_signs() -> None:
    assert money.round_half_even(5, 2) == 2
    assert money.round_half_even(-5, 2) == -2
    assert money.round_half_even(7, 2) == 4
    assert money.round_half_even(-7, 2) == -4


def test_allocation_keeps_every_minor_unit() -> None:
    parts = money.allocate(1001, "USD", [3, 3, 3])
    assert parts == [334, 334, 333]
    assert sum(parts) == 1001


def test_errors_carry_the_spec_code() -> None:
    with pytest.raises(money.SpecError) as exc:
        money.add(money.MAX_MINOR, 1, "USD")
    assert exc.value.code == "overflow"
    assert run("divide", ["1", "2"]) == "error:unknown_operation"
    assert run("add", ["1.5", "2", "USD"]) == "error:invalid_amount"


def test_split_crosses_the_year_end() -> None:
    assert len(dates.split_by_month("2024-12-31", "2025-01-02")) == 2
