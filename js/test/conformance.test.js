// Every row of the shared specification, spec/vectors.tsv, must give exactly the expected answer.
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { test } from "node:test";
import { run } from "../src/evaluate.js";

const rows = readFileSync(new URL("../../spec/vectors.tsv", import.meta.url), "utf8")
  .split(/\r?\n/)
  .filter((l) => l.trim() !== "" && !l.startsWith("#"))
  .map((l) => l.split("\t"));

test("the spec has at least 70 rows", () => {
  assert.ok(rows.length >= 70, `${rows.length} rows`);
});

for (const [id = "", expected = "", op = "", ...args] of rows) {
  test(`${id}: ${op} ${args.join(" ")} -> ${expected}`, () => {
    assert.equal(run(op, args), expected);
  });
}
