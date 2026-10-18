# Contributing

Thanks for helping. This repository holds one small library in three languages (`java/`,
`python/`, `js/`) and one shared specification; issues and pull requests are welcome.

## Set up and check your change

Needs JDK 21+, Maven 3.9+, Python 3.11+, Node.js 24+ and make. Use a virtualenv inside the repo
(`.venv/`, git-ignored).

```bash
python -m venv .venv && . .venv/bin/activate   # Windows: .venv\Scripts\activate
make setup    # Maven dependencies, pip install -e "./python[dev]", npm ci
make lint     # Spotless + javac -Werror, ruff + mypy --strict, tsc strict
make test     # the spec and library tests in all three languages
make bugs     # every seeded bug changes its witness row; clean code passes every row
make audit    # OSV.dev, pip-audit, npm audit
make seeded   # all 20 bugs applied, in .tmp/seeded
```

A pull request is ready when `make lint test bugs` pass and CI is green.

## Guidelines

- Behaviour changes start in `spec/vectors.tsv`; all three implementations must agree before a
  change is merged.
- A new seeded bug needs a catalog entry whose find text occurs exactly once, a realistic title, a
  category, and a witness row it changes. Keep the 7/7/6 split or update the catalog test.
- Keep the library free of runtime dependencies (Python's `tzdata` is the exception).
- Significant design changes need an ADR in `docs/adr/` (copy `0001` for the format).
- Keep function comments to one short phrase; let names and tests explain the rest.
- Report security problems privately, as described in [SECURITY.md](SECURITY.md).

By contributing you agree that your work is released under the [MIT License](LICENSE).
