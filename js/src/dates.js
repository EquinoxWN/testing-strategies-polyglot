// Date ranges with an excluded end date, and UTC instants to local dates in a time zone.
import { SpecError } from "./money.js";

const DAY_MS = 86_400_000;
const INSTANT = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$/;
const ZONE = /^[A-Za-z_]+(\/[A-Za-z_+\-0-9]+)*$/;

/**
 * Midnight UTC of a calendar date, in milliseconds (month is 1-based).
 * @param {number} y
 * @param {number} m
 * @param {number} d
 */
function utc(y, m, d) {
  return Date.UTC(y, m - 1, d);
}

/**
 * A strict ISO date (YYYY-MM-DD) as milliseconds since the epoch.
 * @param {string} text
 * @returns {number}
 */
export function parseDate(text) {
  const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(text);
  if (!match) throw new SpecError("invalid_date");
  const [y, m, d] = [Number(match[1]), Number(match[2]), Number(match[3])];
  const ms = utc(y, m, d);
  const back = new Date(ms);
  if (back.getUTCFullYear() !== y || back.getUTCMonth() + 1 !== m || back.getUTCDate() !== d) {
    throw new SpecError("invalid_date"); // e.g. 2023-02-29 would silently roll over to March 1
  }
  return ms;
}

/**
 * ISO text of a UTC midnight.
 * @param {number} ms
 */
export function isoDate(ms) {
  return new Date(ms).toISOString().slice(0, 10);
}

/**
 * A range [start, end); start after end is an error.
 * @param {string} start
 * @param {string} end
 * @returns {[number, number]}
 */
function range(start, end) {
  const s = parseDate(start);
  const e = parseDate(end);
  if (s > e) throw new SpecError("invalid_range");
  return [s, e];
}

/**
 * Number of days in [start, end).
 * @param {string} start
 * @param {string} end
 */
export function days(start, end) {
  const [s, e] = range(start, end);
  return Math.round((e - s) / DAY_MS);
}

/**
 * Whether day is in [start, end).
 * @param {string} start
 * @param {string} end
 * @param {string} day
 */
export function contains(start, end, day) {
  const [s, e] = range(start, end);
  const d = parseDate(day);
  return s <= d && d < e;
}

/**
 * Whether two ranges share a day; empty ranges overlap nothing.
 * @param {string} s1
 * @param {string} e1
 * @param {string} s2
 * @param {string} e2
 */
export function overlaps(s1, e1, s2, e2) {
  const [a, b] = range(s1, e1);
  const [c, d] = range(s2, e2);
  if (a === b || c === d) return false;
  return a < d && c < b;
}

/**
 * Pieces of [start, end), each inside one calendar month.
 * @param {string} start
 * @param {string} end
 * @returns {[string, string][]}
 */
export function splitByMonth(start, end) {
  let [s, e] = range(start, end);
  /** @type {[string, string][]} */
  const pieces = [];
  while (s < e) {
    const cur = new Date(s);
    const y = cur.getUTCFullYear();
    const m = cur.getUTCMonth() + 1;
    const firstOfNext = m === 12 ? utc(y + 1, 1, 1) : utc(y, m + 1, 1);
    const pieceEnd = Math.min(firstOfNext, e);
    pieces.push([isoDate(s), isoDate(pieceEnd)]);
    s = pieceEnd;
  }
  return pieces;
}

/**
 * The calendar date of a UTC instant in an IANA time zone.
 * @param {string} instant
 * @param {string} zone
 */
export function localDate(instant, zone) {
  if (!INSTANT.test(instant)) throw new SpecError("invalid_date");
  const moment = new Date(instant);
  if (Number.isNaN(moment.getTime())) throw new SpecError("invalid_date");
  if (!ZONE.test(zone)) throw new SpecError("invalid_zone");
  let formatter;
  try {
    formatter = new Intl.DateTimeFormat("en-CA", { timeZone: zone, year: "numeric", month: "2-digit", day: "2-digit" });
  } catch {
    throw new SpecError("invalid_zone");
  }
  return formatter.format(moment);
}
