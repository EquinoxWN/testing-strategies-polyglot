.PHONY: setup lint test bugs seeded audit ci

PY ?= python
PYTHON3 ?= python3
# MVNLOCAL (set by the author's repoenv helper) keeps the Maven repository inside the repo; empty in CI.
MVN = mvn -B -q $(MVNLOCAL)

setup:
	cd java && $(MVN) -DskipTests dependency:resolve
	$(PY) -m pip install --upgrade pip && $(PY) -m pip install -e "./python[dev]"
	cd js && npm ci

# Java: enforcer, Spotless, javac -Xlint:all -Werror. Python: ruff, ruff format, mypy --strict.
# JavaScript: tsc strict over JSDoc types.
lint:
	cd java && $(MVN) -DskipTests compile
	cd python && $(PY) -m ruff check . && $(PY) -m ruff format --check . && $(PY) -m mypy
	$(PY) -m ruff check --config python/pyproject.toml scripts && $(PY) -m mypy --strict scripts/bugs.py
	cd js && npm run lint

# Each language runs the shared spec (spec/vectors.tsv) plus a few library tests;
# Python also checks the bug catalog.
test:
	cd java && $(MVN) verify
	cd python && $(PY) -m pytest -q
	cd js && npm test

# Clean code passes the spec in all three languages, and each of the 20 seeded bugs changes its witness row.
bugs:
	$(PY) scripts/bugs.py verify

# The seeded tree, generated on demand: all 20 bugs applied, written to .tmp/seeded (not kept as a branch).
seeded:
	rm -rf .tmp/seeded && $(PY) scripts/bugs.py materialize .tmp/seeded

# Known vulnerabilities: OSV.dev for Maven, pip-audit for Python, npm audit for JavaScript.
audit:
	cd java && $(MVN) dependency:list -DincludeScope=test -DoutputFile=target/dependencies.txt
	$(PYTHON3) scripts/osv_audit.py Maven java/target/dependencies.txt
	$(PY) -m pip_audit --skip-editable --cache-dir .tmp/pip-audit
	cd js && npm audit --audit-level=low

ci: setup lint test bugs
