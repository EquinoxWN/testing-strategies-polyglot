# RFC 0001: testing-strategies-polyglot design

- **Status:** Accepted (M1 built)
- **Author:** EquinoxWN
- **Created:** 2026-10-18

## Problem (Define)

Teams measure test quality with line coverage, yet bugs still ship at 90% coverage: a rounding mode,
a time zone, an off-by-one at a month end. Choosing between example tests, property tests and
mutation testing is usually argued from opinion. This project builds the evidence: one small library
with realistic risk (money and dates) in three languages, a catalog of realistic bugs, and later a
measurement of which technique catches which bug and at what cost.

Users: engineering leads and staff engineers setting a team's testing standard; developers who want
to see how property and mutation testing compare in Java, Python and JavaScript.

### Critical-to-quality measures

| CTQ | Target (M1) | How it is measured |
|---|---|---|
| Same behaviour in three languages | Java, Python and JavaScript give the same answer on every spec row | each language's conformance test over `spec/vectors.tsv` (74 rows), and `scripts/bugs.py verify` through the three evaluators |
| Realistic bugs, each real | 20 bugs over rounding, overflow, off-by-one, time zones, allocation, parsing and formatting; each changes at least one spec answer | `scripts/bugs.py verify`: 20/20 change their witness row |
| Bugs apply cleanly | each bug's find text occurs exactly once in clean code; all 20 apply together | `tests/test_bug_catalog.py`, `make seeded` |
| Clean code is clean | 0 lint, type or audit findings in any language | Spotless + javac `-Werror`, ruff + mypy strict, tsc strict; OSV, pip-audit, npm audit |

## Goals

- M1: the library (money in integer minor units: parse, add, subtract, half-even multiply, allocate,
  format; date ranges: days, contains, overlaps, split by month, local date of an instant in a time
  zone) in Java 21, Python 3.11+ and Node.js 24, with one shared specification.
- Twenty realistic bugs, seeded apart from the clean code, each proven to change behaviour.

## Non-goals

- Property tests and mutation testing (M2); the technique-by-bug matrix and the strategy guide (M3).
- A complete money or calendar library: currencies are USD, EUR, JPY and BHD; dates are ISO
  calendar dates.

## Design

```
spec/vectors.tsv (74 rows: id, expected, operation, arguments)
   |-- java/   Money, DateRanges, Evaluate      (JUnit: ConformanceTest reads the TSV)
   |-- python/ money, dates, evaluate           (pytest: test_conformance reads the TSV)
   |-- js/     money.js, dates.js, evaluate.js  (node --test: conformance.test.js reads the TSV)
bugs/catalog.toml (20 x {language, file, find, replace, witness})
   scripts/bugs.py verify       copy -> apply one bug -> run all rows through that language's evaluator
   scripts/bugs.py materialize  all 20 bugs applied to a copy: the seeded tree
```

- **Money:** integer minor units up to 2^53 - 1 in every language (the largest integer JavaScript
  numbers hold exactly), so overflow means the same thing everywhere; BigInteger and BigInt where a
  product can exceed it. Multiplication by a decimal factor rounds half-even. Allocation splits by
  ratios and gives leftover units to the first parts with a non-zero ratio.
- **Dates:** half-open ranges [start, end); empty ranges overlap nothing; strict ISO parsing (no
  2023-02-29); local dates through each platform's IANA time zone database (`java.time`,
  `zoneinfo` + `tzdata`, `Intl.DateTimeFormat`).
- **Evaluators:** one text protocol for all three (tab-separated operation and arguments in,
  `ok:<value>` or `error:<code>` out), so one spec file and one harness drive every language
  ([ADR 0002](../adr/0002-one-spec-three-evaluators.md)).
- **Seeded bugs:** exact find-and-replace edits, each with a witness spec row
  ([ADR 0003](../adr/0003-seeded-bugs-as-checked-patches.md)).

## Alternatives considered

| Option | Why not (yet) |
|---|---|
| A separate test suite per language, written by hand | Three suites drift apart; differences in behaviour would be invisible. One spec makes the implementations comparable, which the M3 matrix needs. |
| Seed bugs on a separate git branch | The usual form and what the backlog first said, but every repository here keeps a single `main` branch, and a branch cannot check itself. Catalog entries are checked for applying exactly once and for changing a result, and the seeded tree is generated from them on demand. |
| Mutation testing alone instead of hand-seeded bugs | Mutants are mostly syntactic (flip `<` to `<=`); real bugs such as using the machine's time zone or binary floating point are not mutants. M2 uses both. |
| JSON for the spec | Needs a parser in Java (no dependency allowed in the library); TSV is read with a split in all three languages. |

## Measurement plan (Measure)

- Each language's conformance suite; `scripts/bugs.py verify` (clean pass rate, witness change and
  number of rows each bug changes); lint, types and audits.
- M2: property tests (jqwik, Hypothesis, fast-check) and mutation scores (PIT, mutmut, Stryker).
- M3: which technique catches which of the 20 bugs, and the run time of each technique.

## Milestones

- **M1 (done):** RFC; the library in three languages with one spec; 20 seeded bugs.
- **M2:** example, property and mutation tests per language; mutation scores beyond line coverage.
- **M3:** bug-by-technique matrix with costs; testing strategy guide per risk level.

## Risks and open questions

- The spec rows include each bug's witness, so the example suite catches all 20 bugs by
  construction. M3 must measure techniques with suites that were not written from the bug list
  (for example with a hidden set of rows used only for scoring).
- JavaScript's S3 bug (machine time zone) is only visible on machines not on UTC-5; its witness was
  chosen so it fails on UTC and on UTC+7, the two zones used here.
- The seeded tree exists only when generated (`make seeded`); tools that need it in M2 and M3 must
  generate it first.
