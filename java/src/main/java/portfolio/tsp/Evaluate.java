package portfolio.tsp;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintStream;
import java.nio.charset.StandardCharsets;
import java.time.LocalDate;
import java.util.Arrays;
import java.util.List;
import java.util.stream.Collectors;

/**
 * Evaluates one spec operation from text arguments and returns {@code ok:<value>} or
 * {@code error:<code>}. {@code main} reads tab-separated lines (operation, arguments...) on stdin
 * and prints one result line each, the same protocol as the Python and JavaScript versions.
 */
public final class Evaluate {
    private Evaluate() {}

    /** One operation; never throws for bad input. */
    public static String run(String op, List<String> a) {
        try {
            return "ok:"
                    + switch (op + "/" + a.size()) {
                        case "parse/2" -> String.valueOf(Money.parse(a.get(0), a.get(1)));
                        case "add/3" -> String.valueOf(Money.add(integer(a.get(0)), integer(a.get(1)), a.get(2)));
                        case "subtract/3" ->
                            String.valueOf(Money.subtract(integer(a.get(0)), integer(a.get(1)), a.get(2)));
                        case "multiply/3" -> String.valueOf(Money.multiply(integer(a.get(0)), a.get(1), a.get(2)));
                        case "allocate/3" ->
                            Arrays.stream(Money.allocate(integer(a.get(0)), a.get(1), ratios(a.get(2))))
                                    .mapToObj(Long::toString)
                                    .collect(Collectors.joining(","));
                        case "format/2" -> Money.format(integer(a.get(0)), a.get(1));
                        case "days/2" -> String.valueOf(DateRanges.days(a.get(0), a.get(1)));
                        case "contains/3" -> String.valueOf(DateRanges.contains(a.get(0), a.get(1), a.get(2)));
                        case "overlaps/4" ->
                            String.valueOf(DateRanges.overlaps(a.get(0), a.get(1), a.get(2), a.get(3)));
                        case "split/2" ->
                            DateRanges.splitByMonth(a.get(0), a.get(1)).stream()
                                    .map(r -> r[0] + "/" + r[1])
                                    .collect(Collectors.joining(","));
                        case "localdate/2" -> {
                            LocalDate d = DateRanges.localDate(a.get(0), a.get(1));
                            yield d.toString();
                        }
                        default -> throw new SpecException("unknown_operation");
                    };
        } catch (SpecException e) {
            return "error:" + e.code();
        }
    }

    /** An integer argument; anything else is an invalid amount. */
    private static long integer(String text) {
        try {
            return Long.parseLong(text);
        } catch (NumberFormatException e) {
            throw new SpecException("invalid_amount");
        }
    }

    /** Comma-separated ratios. */
    private static long[] ratios(String text) {
        try {
            return Arrays.stream(text.split(",", -1)).mapToLong(Long::parseLong).toArray();
        } catch (NumberFormatException e) {
            throw new SpecException("invalid_ratios");
        }
    }

    /** Answers each stdin line. */
    public static void main(String[] args) throws IOException {
        PrintStream out = new PrintStream(System.out, true, StandardCharsets.UTF_8);
        BufferedReader in = new BufferedReader(new InputStreamReader(System.in, StandardCharsets.UTF_8));
        for (String line = in.readLine(); line != null; line = in.readLine()) {
            List<String> parts = Arrays.asList(line.split("\t", -1));
            out.println(run(parts.get(0), parts.subList(1, parts.size())));
        }
    }
}
