// Money in integer minor units (BigInt): parse, add, subtract, multiply (half-even), allocate, format.

/** @type {Record<string, number>} */
const SCALES = { USD: 2, EUR: 2, JPY: 0, BHD: 3 };

/** 2^53 - 1: the same limit in Java, Python and JavaScript. */
export const MAX_MINOR = 9007199254740991n;

const FACTOR = /^-?\d{1,9}(\.\d{1,9})?$/;

/** A specification error; the code is shared by all three implementations. */
export class SpecError extends Error {
  /** @param {string} code */
  constructor(code) {
    super(code);
    this.code = code;
  }
}

/**
 * Decimal places of a currency.
 * @param {string} currency
 * @returns {number}
 */
export function scale(currency) {
  if (!Object.hasOwn(SCALES, currency)) throw new SpecError("unknown_currency");
  return /** @type {number} */ (SCALES[currency]);
}

/**
 * The amount, or an overflow error outside +/- MAX_MINOR.
 * @param {bigint} minor
 * @returns {bigint}
 */
function checked(minor) {
  if (minor > MAX_MINOR || minor < -MAX_MINOR) throw new SpecError("overflow");
  return minor;
}

/**
 * Parses a plain decimal like -12.34 into minor units.
 * @param {string} text
 * @param {string} currency
 * @returns {bigint}
 */
export function parse(text, currency) {
  const digits = scale(currency);
  const pattern = digits > 0 ? new RegExp(`^-?\\d{1,16}(\\.\\d{1,${digits}})?$`) : /^-?\d{1,16}$/;
  if (!pattern.test(text)) throw new SpecError("invalid_amount");
  const negative = text.startsWith("-");
  const [whole = "0", frac = ""] = (negative ? text.slice(1) : text).split(".");
  const minor = BigInt(whole) * 10n ** BigInt(digits) + BigInt((frac + "0".repeat(digits)).slice(0, digits) || "0");
  return checked(negative ? -minor : minor);
}

/**
 * a + b in one currency.
 * @param {bigint} a
 * @param {bigint} b
 * @param {string} currency
 */
export function add(a, b, currency) {
  scale(currency);
  return checked(a + b);
}

/**
 * a - b in one currency.
 * @param {bigint} a
 * @param {bigint} b
 * @param {string} currency
 */
export function subtract(a, b, currency) {
  scale(currency);
  return checked(a - b);
}

/**
 * numerator / denominator rounded to the nearest integer, ties to even.
 * @param {bigint} numerator
 * @param {bigint} denominator positive
 * @returns {bigint}
 */
export function roundHalfEven(numerator, denominator) {
  let q = numerator / denominator; // BigInt division truncates toward zero
  let r = numerator % denominator;
  if (r < 0n) {
    q -= 1n; // floor division, so 0 <= r < denominator
    r += denominator;
  }
  const twice = 2n * r;
  if (twice > denominator || (twice === denominator && q % 2n !== 0n)) q += 1n;
  return q;
}

/**
 * minor x factor (a decimal string), rounded half-even to whole minor units.
 * @param {bigint} minor
 * @param {string} currency
 * @param {string} factor
 */
export function multiply(minor, currency, factor) {
  scale(currency);
  if (!FACTOR.test(factor)) throw new SpecError("invalid_factor");
  const [whole = "0", frac = ""] = factor.split(".");
  const numerator = BigInt(whole + frac);
  const denominator = 10n ** BigInt(frac.length);
  return checked(roundHalfEven(minor * numerator, denominator));
}

/**
 * Splits an amount by ratios without losing a minor unit; leftovers go to the first eligible parts.
 * @param {bigint} minor
 * @param {string} currency
 * @param {bigint[]} ratios
 * @returns {bigint[]}
 */
export function allocate(minor, currency, ratios) {
  scale(currency);
  const total = ratios.reduce((s, r) => s + r, 0n);
  if (ratios.length < 1 || ratios.length > 100 || ratios.some((r) => r < 0n) || total === 0n) {
    throw new SpecError("invalid_ratios");
  }
  const magnitude = minor < 0n ? -minor : minor;
  const parts = ratios.map((r) => (magnitude * r) / total);
  let leftover = magnitude - parts.reduce((s, p) => s + p, 0n);
  for (let i = 0; i < ratios.length && leftover > 0n; i++) {
    if (/** @type {bigint} */ (ratios[i]) > 0n) {
      parts[i] = /** @type {bigint} */ (parts[i]) + 1n;
      leftover -= 1n;
    }
  }
  return minor < 0n ? parts.map((p) => -p) : parts;
}

/**
 * Formats like "-12.34 USD"; JPY has no decimals, BHD three.
 * @param {bigint} minor
 * @param {string} currency
 */
export function format(minor, currency) {
  const digits = scale(currency);
  const sign = minor < 0n ? "-" : "";
  const magnitude = minor < 0n ? -minor : minor;
  const unit = 10n ** BigInt(digits);
  const body = digits > 0 ? `${magnitude / unit}.${String(magnitude % unit).padStart(digits, "0")}` : `${magnitude}`;
  return `${sign}${body} ${currency}`;
}
