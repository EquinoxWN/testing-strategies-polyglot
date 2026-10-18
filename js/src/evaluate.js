// Evaluates one spec operation from text arguments and returns "ok:<value>" or "error:<code>".
// Run as `node src/evaluate.js`: reads tab-separated lines (operation, arguments...) on stdin and
// prints one result line each, the same protocol as the Java and Python versions.
import { createInterface } from "node:readline";
import { pathToFileURL } from "node:url";
import { contains, days, localDate, overlaps, splitByMonth } from "./dates.js";
import { SpecError, add, allocate, format, multiply, parse, subtract } from "./money.js";

/**
 * An integer argument; anything else is an invalid amount.
 * @param {string | undefined} text
 * @returns {bigint}
 */
function integer(text) {
  if (text === undefined || !/^-?\d{1,19}$/.test(text)) throw new SpecError("invalid_amount");
  return BigInt(text);
}

/**
 * Comma-separated ratios.
 * @param {string} text
 * @returns {bigint[]}
 */
function ratios(text) {
  return text.split(",").map((r) => {
    if (!/^-?\d{1,19}$/.test(r)) throw new SpecError("invalid_ratios");
    return BigInt(r);
  });
}

/**
 * One operation; never throws for bad input.
 * @param {string} op
 * @param {string[]} a
 * @returns {string}
 */
export function run(op, a) {
  /** @param {number} i */
  const arg = (i) => /** @type {string} */ (a[i]);
  try {
    switch (`${op}/${a.length}`) {
      case "parse/2":
        return `ok:${parse(arg(0), arg(1))}`;
      case "add/3":
        return `ok:${add(integer(a[0]), integer(a[1]), arg(2))}`;
      case "subtract/3":
        return `ok:${subtract(integer(a[0]), integer(a[1]), arg(2))}`;
      case "multiply/3":
        return `ok:${multiply(integer(a[0]), arg(1), arg(2))}`;
      case "allocate/3":
        return `ok:${allocate(integer(a[0]), arg(1), ratios(arg(2))).join(",")}`;
      case "format/2":
        return `ok:${format(integer(a[0]), arg(1))}`;
      case "days/2":
        return `ok:${days(arg(0), arg(1))}`;
      case "contains/3":
        return `ok:${contains(arg(0), arg(1), arg(2))}`;
      case "overlaps/4":
        return `ok:${overlaps(arg(0), arg(1), arg(2), arg(3))}`;
      case "split/2":
        return `ok:${splitByMonth(arg(0), arg(1)).map(([s, e]) => `${s}/${e}`).join(",")}`;
      case "localdate/2":
        return `ok:${localDate(arg(0), arg(1))}`;
      default:
        return "error:unknown_operation";
    }
  } catch (e) {
    if (e instanceof SpecError) return `error:${e.code}`;
    throw e;
  }
}

/** Answers each stdin line. */
async function main() {
  const lines = createInterface({ input: process.stdin, crlfDelay: Infinity });
  for await (const line of lines) {
    const [op = "", ...args] = line.split("\t");
    process.stdout.write(`${run(op, args)}\n`);
  }
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  await main();
}
