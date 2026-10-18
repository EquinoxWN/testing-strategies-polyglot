"""Every row of the shared specification, spec/vectors.tsv, must give exactly the expected answer."""

from __future__ import annotations

from pathlib import Path

import pytest

from testing_strategies_polyglot.evaluate import run

VECTORS = Path(__file__).resolve().parents[2] / "spec" / "vectors.tsv"
ROWS = [
    line.split("\t")
    for line in VECTORS.read_text(encoding="utf-8").splitlines()
    if line.strip() and not line.startswith("#")
]


def test_the_spec_has_at_least_70_rows() -> None:
    assert len(ROWS) >= 70


@pytest.mark.parametrize("row", ROWS, ids=[r[0] for r in ROWS])
def test_matches_the_spec(row: list[str]) -> None:
    _, expected, op, *args = row
    assert run(op, args) == expected
