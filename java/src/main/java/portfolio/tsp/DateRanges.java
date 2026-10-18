package portfolio.tsp;

import java.time.DateTimeException;
import java.time.Instant;
import java.time.LocalDate;
import java.time.ZoneId;
import java.time.format.DateTimeFormatter;
import java.time.format.ResolverStyle;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.List;

/** Date ranges with an excluded end date, and UTC instants to local dates in a time zone. */
public final class DateRanges {
    private static final DateTimeFormatter DATE =
            DateTimeFormatter.ofPattern("uuuu-MM-dd").withResolverStyle(ResolverStyle.STRICT);

    private DateRanges() {}

    /** A strict ISO date (YYYY-MM-DD). */
    public static LocalDate parseDate(String text) {
        if (!text.matches("^\\d{4}-\\d{2}-\\d{2}$")) {
            throw new SpecException("invalid_date");
        }
        try {
            return LocalDate.parse(text, DATE);
        } catch (DateTimeException e) {
            throw new SpecException("invalid_date");
        }
    }

    /** A range [start, end); start after end is an error. */
    static LocalDate[] range(String start, String end) {
        LocalDate s = parseDate(start);
        LocalDate e = parseDate(end);
        if (s.isAfter(e)) {
            throw new SpecException("invalid_range");
        }
        return new LocalDate[] {s, e};
    }

    /** Number of days in [start, end). */
    public static long days(String start, String end) {
        LocalDate[] r = range(start, end);
        return ChronoUnit.DAYS.between(r[0], r[1]);
    }

    /** Whether day is in [start, end). */
    public static boolean contains(String start, String end, String day) {
        LocalDate[] r = range(start, end);
        LocalDate d = parseDate(day);
        return !d.isBefore(r[0]) && d.isBefore(r[1]);
    }

    /** Whether two ranges share a day; empty ranges overlap nothing. */
    public static boolean overlaps(String s1, String e1, String s2, String e2) {
        LocalDate[] a = range(s1, e1);
        LocalDate[] b = range(s2, e2);
        if (a[0].equals(a[1]) || b[0].equals(b[1])) {
            return false;
        }
        return a[0].isBefore(b[1]) && b[0].isBefore(a[1]);
    }

    /** Pieces of [start, end), each inside one calendar month. */
    public static List<LocalDate[]> splitByMonth(String start, String end) {
        LocalDate[] r = range(start, end);
        List<LocalDate[]> pieces = new ArrayList<>();
        LocalDate s = r[0];
        while (s.isBefore(r[1])) {
            LocalDate firstOfNext = s.withDayOfMonth(1).plusMonths(1);
            LocalDate pieceEnd = firstOfNext.isBefore(r[1]) ? firstOfNext : r[1];
            pieces.add(new LocalDate[] {s, pieceEnd});
            s = pieceEnd;
        }
        return pieces;
    }

    /** The calendar date of a UTC instant in an IANA time zone. */
    public static LocalDate localDate(String instant, String zone) {
        if (!instant.matches("^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}:\\d{2}Z$")) {
            throw new SpecException("invalid_date");
        }
        Instant moment;
        try {
            moment = Instant.parse(instant);
        } catch (DateTimeException e) {
            throw new SpecException("invalid_date");
        }
        ZoneId tz;
        try {
            tz = ZoneId.of(zone);
        } catch (DateTimeException e) {
            throw new SpecException("invalid_zone");
        }
        return LocalDate.ofInstant(moment, tz);
    }
}
