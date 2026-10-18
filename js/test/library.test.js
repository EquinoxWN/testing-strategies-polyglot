// A few direct checks of the library API next to the spec rows.
import assert from "node:assert/strict";
import { test } from "node:test";
import { splitByMonth } from "../src/dates.js";
import { run } from "../src/evaluate.js";
import { MAX_MINOR, SpecError, add, allocate, roundHalfEven } from "../src/money.js";

test("round half even on both signs", () => {
  assert.equal(roundHalfEven(5n, 2n), 2n);
  assert.equal(roundHalfEven(-5n, 2n), -2n);
  assert.equal(roundHalfEven(7n, 2n), 4n);
  assert.equal(roundHalfEven(-7n, 2n), -4n);
});

test("allocation keeps every minor unit", () => {
  const parts = allocate(1001n, "USD", [3n, 3n, 3n]);
  assert.deepEqual(parts, [334n, 334n, 333n]);
  assert.equal(parts.reduce((s, p) => s + p, 0n), 1001n);
});

test("errors carry the spec code", () => {
  assert.throws(() => add(MAX_MINOR, 1n, "USD"), (e) => e instanceof SpecError && e.code === "overflow");
  assert.equal(run("divide", ["1", "2"]), "error:unknown_operation");
  assert.equal(run("add", ["1.5", "2", "USD"]), "error:invalid_amount");
});

test("split crosses the year end", () => {
  assert.equal(splitByMonth("2024-12-31", "2025-01-02").length, 2);
});
