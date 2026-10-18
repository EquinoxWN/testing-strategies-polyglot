package portfolio.tsp;

import java.math.BigInteger;
import java.util.Map;
import java.util.regex.Pattern;

/** Money in integer minor units: parse, add, subtract, multiply (half-even), allocate, format. */
public final class Money {
    /** 2^53 - 1: the same limit in Java, Python and JavaScript. */
    public static final long MAX_MINOR = 9_007_199_254_740_991L;

    private static final Map<String, Integer> SCALES = Map.of("USD", 2, "EUR", 2, "JPY", 0, "BHD", 3);
    private static final Pattern FACTOR = Pattern.compile("^-?\\d{1,9}(\\.\\d{1,9})?$");
    private static final BigInteger TWO = BigInteger.TWO;

    private Money() {}

    /** Decimal places of a currency. */
    public static int scale(String currency) {
        Integer s = SCALES.get(currency);
        if (s == null) {
            throw new SpecException("unknown_currency");
        }
        return s;
    }

    /** The amount, or an overflow error outside +/- MAX_MINOR. */
    static long checked(BigInteger minor) {
        if (minor.abs().compareTo(BigInteger.valueOf(MAX_MINOR)) > 0) {
            throw new SpecException("overflow");
        }
        return minor.longValueExact();
    }

    /** Parses a plain decimal like -12.34 into minor units. */
    public static long parse(String text, String currency) {
        int digits = scale(currency);
        String pattern = digits > 0 ? "^-?\\d{1,16}(\\.\\d{1," + digits + "})?$" : "^-?\\d{1,16}$";
        if (!text.matches(pattern)) {
            throw new SpecException("invalid_amount");
        }
        boolean negative = text.startsWith("-");
        String body = negative ? text.substring(1) : text;
        int dot = body.indexOf('.');
        String whole = dot < 0 ? body : body.substring(0, dot);
        String frac = dot < 0 ? "" : body.substring(dot + 1);
        BigInteger minor = new BigInteger(whole)
                .multiply(BigInteger.TEN.pow(digits))
                .add(new BigInteger("0" + (frac + "0".repeat(digits)).substring(0, digits)));
        return checked(negative ? minor.negate() : minor);
    }

    /** a + b in one currency. */
    public static long add(long a, long b, String currency) {
        scale(currency);
        return checked(BigInteger.valueOf(a).add(BigInteger.valueOf(b)));
    }

    /** a - b in one currency. */
    public static long subtract(long a, long b, String currency) {
        scale(currency);
        return checked(BigInteger.valueOf(a).subtract(BigInteger.valueOf(b)));
    }

    /** numerator / denominator rounded to the nearest integer, ties to even. */
    static BigInteger roundHalfEven(BigInteger numerator, BigInteger denominator) {
        BigInteger[] qr = numerator.divideAndRemainder(denominator);
        BigInteger q = qr[0];
        BigInteger r = qr[1];
        if (r.signum() < 0) { // floor division, so 0 <= r < denominator
            q = q.subtract(BigInteger.ONE);
            r = r.add(denominator);
        }
        int cmp = r.multiply(TWO).compareTo(denominator);
        if (cmp > 0 || (cmp == 0 && q.testBit(0))) {
            q = q.add(BigInteger.ONE);
        }
        return q;
    }

    /** minor x factor (a decimal string), rounded half-even to whole minor units. */
    public static long multiply(long minor, String currency, String factor) {
        scale(currency);
        if (!FACTOR.matcher(factor).matches()) {
            throw new SpecException("invalid_factor");
        }
        int dot = factor.indexOf('.');
        String frac = dot < 0 ? "" : factor.substring(dot + 1);
        BigInteger numerator = new BigInteger(dot < 0 ? factor : factor.substring(0, dot) + frac);
        BigInteger denominator = BigInteger.TEN.pow(frac.length());
        return checked(roundHalfEven(BigInteger.valueOf(minor).multiply(numerator), denominator));
    }

    /** Splits an amount by ratios without losing a minor unit; leftovers go to the first eligible parts. */
    public static long[] allocate(long minor, String currency, long[] ratios) {
        scale(currency);
        long total = 0;
        for (long r : ratios) {
            if (r < 0) {
                throw new SpecException("invalid_ratios");
            }
            total += r;
        }
        if (ratios.length < 1 || ratios.length > 100 || total == 0) {
            throw new SpecException("invalid_ratios");
        }
        BigInteger magnitude = BigInteger.valueOf(minor).abs();
        long[] parts = new long[ratios.length];
        long leftover = magnitude.longValueExact();
        for (int i = 0; i < ratios.length; i++) {
            parts[i] = magnitude
                    .multiply(BigInteger.valueOf(ratios[i]))
                    .divide(BigInteger.valueOf(total))
                    .longValueExact();
            leftover -= parts[i];
        }
        for (int i = 0; i < ratios.length && leftover > 0; i++) {
            if (ratios[i] > 0) {
                parts[i]++;
                leftover--;
            }
        }
        if (minor < 0) {
            for (int i = 0; i < parts.length; i++) {
                parts[i] = -parts[i];
            }
        }
        return parts;
    }

    /** Formats like {@code -12.34 USD}; JPY has no decimals, BHD three. */
    public static String format(long minor, String currency) {
        int digits = scale(currency);
        String sign = minor < 0 ? "-" : "";
        BigInteger[] wf = BigInteger.valueOf(minor).abs().divideAndRemainder(BigInteger.TEN.pow(digits));
        String body = digits > 0 ? wf[0] + "." + String.format("%0" + digits + "d", wf[1]) : wf[0].toString();
        return sign + body + " " + currency;
    }
}
