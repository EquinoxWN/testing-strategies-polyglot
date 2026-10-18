# Security policy

## Reporting a vulnerability

Please report security problems privately through GitHub:
**Security > Report a vulnerability** on this repository
(`https://github.com/EquinoxWN/testing-strategies-polyglot/security/advisories/new`). Do not open a public issue.

Include what you found, how to reproduce it, and the impact you expect. You will get an answer
within 7 days. Fixes are released as soon as they are ready, and you are credited unless you ask
not to be.

## Supported versions

This project is pre-1.0. Only the latest commit on `main` receives fixes.

## Scope

- **In scope:** the clean library giving a wrong answer (money or dates), input that crashes an
  evaluator or uses unbounded time, and the bug harness writing outside `.tmp/` or running anything
  other than javac, java, node and the repository's Python.
- **Out of scope:** the twenty seeded bugs in `bugs/catalog.toml`: they are wrong on purpose.

## How this repository protects itself

- Amounts are integers in minor units with a range check (2^53 - 1) in every language; inputs are
  matched against strict patterns before parsing; rounding is exact (no binary floating point).
- The harness copies code into `.tmp/bugs/`, applies one edit that must match exactly once, runs the
  evaluator with a timeout, and deletes the copies.
- Runtime dependencies: none for Java and JavaScript; `tzdata` for Python.
- Every GitHub Action is pinned to a full commit SHA, and workflows run with read-only
  permissions and without persisted credentials.
- Dependabot update pull requests are paused (`open-pull-requests-limit: 0`) so the repository keeps a single `main` branch; dependencies are updated by hand and checked by the CI audit.
- CI runs lint, tests and known-vulnerability checks (OSV.dev for Maven, pip-audit, npm audit) on every push and pull request.
