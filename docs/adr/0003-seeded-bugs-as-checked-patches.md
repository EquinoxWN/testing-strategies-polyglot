# ADR 0003: Seeded bugs as checked find-and-replace patches, not a branch

- **Status:** Accepted

## Context

The backlog item for M1 reads: twenty realistic bugs "are seeded on a separate branch". A branch
holding the buggy code is the common form, but:

- every repository in this portfolio keeps a single `main` branch (the owner's rule), so a
  long-lived seeded-bugs branch is not allowed;
- nothing on a branch checks that a seeded bug actually changes behaviour (a bug that is never
  reachable makes every technique look bad);
- rebasing a branch after a change to clean code is manual;
- one branch holding all bugs cannot test one bug at a time.

## Decision

Deviation from the backlog wording: the bugs are not kept on a separate branch. They live on `main`
as data, apart from the clean code, in `bugs/catalog.toml`. Each entry has an id, language, file,
category, title, the exact text to find (it must occur exactly once in clean code), its
replacement, and a witness: a spec row whose answer the bug changes. `scripts/bugs.py`:

- `verify`: runs the clean code of each language through all spec rows, then for each bug copies
  that language's tree into `.tmp/bugs/`, applies only that bug, runs all rows, and checks that the
  witness answer changed; a hang or compile failure counts as a change; scratch copies are deleted.
- `materialize DIR` (`make seeded`, into `.tmp/seeded`): applies all twenty bugs to one copy. This
  seeded tree is generated on demand and deliberately not committed or kept as a branch.

The intent of the backlog item (bugs kept apart from the clean code, so the clean code stays
correct and the buggy version can be tested) is met; only the storage differs.

## Consequences

- Every bug is proven live on every run (20/20 in CI), and the catalog test fails if a code change
  makes a find text disappear or appear twice.
- Bugs can be evaluated one at a time, which the M3 technique matrix needs (a test that fails on a
  tree with all bugs would not say which bug it found).
- The edits are small and readable in the catalog, which doubles as documentation of the bug.
- The repository keeps a single `main` branch; anyone who wants the buggy code runs `make seeded`.
- One seeded bug first produced an infinite loop (a December range never advanced); the harness now
  treats a timeout as a changed answer, and the bug was replaced with a terminating off-by-one so
  the evaluator answers every row.
