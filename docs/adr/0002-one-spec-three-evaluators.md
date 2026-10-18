# ADR 0002: One specification file and one evaluator protocol for all three languages

- **Status:** Accepted

## Context

The project compares testing techniques across Java, Python and JavaScript. That comparison only
means something if the three implementations behave the same: if Python rounded differently from
Java, a bug "caught in Python only" could be a spec difference instead of a technique difference.
Writing three example suites by hand would let them drift.

## Decision

- `spec/vectors.tsv` holds every agreed answer: one row per case with an id, the expected result
  (`ok:<value>` or `error:<code>`), the operation and its arguments, all as text.
- Each language has an `Evaluate` / `evaluate` module that maps an operation and text arguments to
  that text result and never throws for bad input. Its `main` reads rows from stdin and prints one
  result per line.
- Each language's conformance test reads the same TSV and checks every row; the bug harness drives
  the three evaluators as child processes with the same rows.
- Error codes (`overflow`, `invalid_amount`, `invalid_zone`, ...) are part of the spec.

## Consequences

- Adding a case is one line, checked in three languages at once. All 74 rows agree in Java, Python
  and JavaScript; finding a row that needed a new case (100 x 0.545: one of 2 cases among
  7,992 products searched where binary floating point changes the half-even result) took a search over
  candidates, which is recorded in the results.
- TSV keeps the format readable and parseable without libraries, at the cost of encoding lists
  (comma-separated) and ranges (`start/end`) as text.
- The evaluators are test infrastructure in the main source tree; they are small (one switch each)
  and they also give the M2/M3 tools one entry point per language.
