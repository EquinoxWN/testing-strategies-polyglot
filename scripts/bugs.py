"""Seeded-bug harness.

usage: python scripts/bugs.py verify               every bug changes its witness; clean code passes the spec
       python scripts/bugs.py materialize DIR      write the three implementations with all 20 bugs applied

Each language is driven through its own evaluator (stdin: tab-separated operation and arguments;
stdout: ok:<value> or error:<code>), so one spec and one harness cover Java, Python and JavaScript.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import time
import tomllib
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP = {"node_modules", "target", ".venv", "__pycache__", "build", "dist"}
TIMEOUT_S = 60


@dataclass(frozen=True)
class Bug:
    """One catalog entry."""

    id: str
    language: str
    file: str
    category: str
    title: str
    find: str
    replace: str
    witness: str


def catalog() -> list[Bug]:
    """The bugs from bugs/catalog.toml, with unique ids."""
    raw = tomllib.loads((ROOT / "bugs" / "catalog.toml").read_text(encoding="utf-8"))["bug"]
    bugs = [Bug(**b) for b in raw]
    if len({b.id for b in bugs}) != len(bugs):
        raise SystemExit("duplicate bug ids in the catalog")
    return bugs


def vectors() -> list[list[str]]:
    """Spec rows: id, expected, operation, arguments..."""
    lines = (ROOT / "spec" / "vectors.tsv").read_text(encoding="utf-8").splitlines()
    return [line.split("\t") for line in lines if line.strip() and not line.startswith("#")]


def copy_language(lang: str, dest: Path) -> Path:
    """Copy one implementation without build output or dependencies."""
    target = dest / lang
    shutil.copytree(ROOT / lang, target, ignore=lambda _d, names: [n for n in names if n in SKIP])
    return target


def apply(bug: Bug, tree: Path) -> None:
    """Apply one bug; the find text must occur exactly once."""
    path = tree / bug.file
    text = path.read_text(encoding="utf-8")
    count = text.count(bug.find)
    if count != 1:
        raise SystemExit(f"{bug.id}: find text occurs {count} times in {bug.file}, expected exactly once")
    path.write_text(text.replace(bug.find, bug.replace), encoding="utf-8", newline="\n")


def evaluator(lang: str, tree: Path, work: Path) -> list[str]:
    """The command that runs a language's evaluator on a tree (compiling Java first)."""
    if lang == "python":
        src = str(tree / "src")  # put the copy first so it wins over any installed package
        code = f"import sys; sys.path.insert(0, {src!r}); from testing_strategies_polyglot.evaluate import main; main()"
        return [sys.executable, "-c", code]
    if lang == "js":
        return ["node", str(tree / "src" / "evaluate.js")]
    classes = work / "classes"
    sources = [str(p) for p in (tree / "src" / "main" / "java").rglob("*.java")]
    javac = ["javac", "-nowarn", "-d", str(classes), *sources]
    subprocess.run(javac, check=True, timeout=TIMEOUT_S)  # noqa: S603 - JDK tools from PATH
    return ["java", "-Xmx128m", "-XX:-UsePerfData", "-cp", str(classes), "portfolio.tsp.Evaluate"]


def run_spec(lang: str, tree: Path, work: Path) -> dict[str, str]:
    """Answers of one tree for every spec row, keyed by row id."""
    rows = vectors()
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    stdin = "".join("\t".join(r[2:]) + "\n" for r in rows)
    try:
        out = subprocess.run(  # noqa: S603 - fixed commands built above
            evaluator(lang, tree, work),
            input=stdin,
            capture_output=True,
            text=True,
            env=env,
            timeout=TIMEOUT_S,
            check=False,
            encoding="utf-8",
        )
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
        return {r[0]: "crash" for r in rows}  # a hang or a failed compile counts as a changed answer
    answers = out.stdout.splitlines()
    if out.returncode != 0 or len(answers) != len(rows):
        return {r[0]: "crash" for r in rows}
    return {r[0]: a for r, a in zip(rows, answers, strict=True)}


def verify(scratch: Path) -> int:
    """Check clean trees pass the spec and every bug changes its witness; print a table."""
    rows = vectors()
    expected = {r[0]: r[1] for r in rows}
    ok = True
    print(f"spec: {len(rows)} rows")
    for lang in ("java", "python", "js"):
        work = scratch / f"clean-{lang}"
        tree = copy_language(lang, work)
        t0 = time.perf_counter()
        answers = run_spec(lang, tree, work)
        passed = sum(answers[k] == v for k, v in expected.items())
        ok &= passed == len(rows)
        print(f"clean {lang:<6} {passed}/{len(rows)} rows match ({time.perf_counter() - t0:.1f} s)")
    print()
    print(f"{'bug':<4} {'language':<8} {'category':<11} {'witness':<8} {'witness answer':<34} rows changed")
    live = 0
    bugs = catalog()
    for bug in bugs:
        work = scratch / bug.id
        tree = copy_language(bug.language, work)
        apply(bug, tree)
        answers = run_spec(bug.language, tree, work)
        changed = sum(answers[k] != v for k, v in expected.items())
        got = answers[bug.witness]
        is_live = got != expected[bug.witness]
        live += is_live
        ok &= is_live
        mark = "" if is_live else "   NOT LIVE"
        print(
            f"{bug.id:<4} {bug.language:<8} {bug.category:<11} {bug.witness:<8} {got[:34]:<34} "
            f"{changed}/{len(rows)}{mark}"
        )
    print(
        f"RESULT bugs: {live}/{len(bugs)} seeded bugs change their witness row; "
        f"clean Java, Python and JS pass all {len(rows)} rows"
    )
    return 0 if ok else 1


def materialize(dest: Path) -> int:
    """Write the three implementations with every bug applied (the seeded tree, generated on demand)."""
    if dest.exists() and any(dest.iterdir()):
        raise SystemExit(f"{dest} is not empty")
    for lang in ("java", "python", "js"):
        copy_language(lang, dest)
    for bug in catalog():
        apply(bug, dest / bug.language)
    print(f"wrote {dest} with {len(catalog())} bugs applied")
    return 0


def main() -> int:
    """Dispatch the sub-command."""
    if len(sys.argv) == 2 and sys.argv[1] == "verify":
        scratch = ROOT / ".tmp" / "bugs"
        shutil.rmtree(scratch, ignore_errors=True)
        scratch.mkdir(parents=True)
        try:
            return verify(scratch)
        finally:
            shutil.rmtree(scratch, ignore_errors=True)
    if len(sys.argv) == 3 and sys.argv[1] == "materialize":
        return materialize(Path(sys.argv[2]))
    print(__doc__, file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
