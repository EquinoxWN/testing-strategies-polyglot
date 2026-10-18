"""The seeded-bug catalog is well formed and every bug applies to exactly one place in clean code."""

from __future__ import annotations

import tomllib
from collections import Counter
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[2]
BUGS: list[dict[str, Any]] = tomllib.loads((ROOT / "bugs" / "catalog.toml").read_text(encoding="utf-8"))["bug"]
SPEC_IDS = {
    line.split("\t")[0]
    for line in (ROOT / "spec" / "vectors.tsv").read_text(encoding="utf-8").splitlines()
    if line.strip() and not line.startswith("#")
}


def test_twenty_bugs_across_three_languages() -> None:
    assert len(BUGS) == 20
    assert len({b["id"] for b in BUGS}) == 20
    assert Counter(b["language"] for b in BUGS) == {"java": 7, "python": 7, "js": 6}
    categories = {b["category"] for b in BUGS}
    assert {"rounding", "time zone", "overflow", "off-by-one"} <= categories


@pytest.mark.parametrize("bug", BUGS, ids=[b["id"] for b in BUGS])
def test_bug_targets_one_place_and_names_a_spec_row(bug: dict[str, Any]) -> None:
    source = (ROOT / bug["language"] / bug["file"]).read_text(encoding="utf-8")
    assert source.count(bug["find"]) == 1
    assert bug["find"] != bug["replace"]
    assert bug["witness"] in SPEC_IDS
