package portfolio.tsp;

import static org.junit.jupiter.api.Assertions.assertArrayEquals;
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;

import java.math.BigInteger;
import java.util.List;
import org.junit.jupiter.api.Test;

/** A few direct checks of the library API next to the spec rows. */
class LibraryTest {

    @Test
    void roundHalfEvenOnBothSigns() {
        assertEquals(BigInteger.valueOf(2), Money.roundHalfEven(BigInteger.valueOf(5), BigInteger.TWO));
        assertEquals(BigInteger.valueOf(-2), Money.roundHalfEven(BigInteger.valueOf(-5), BigInteger.TWO));
        assertEquals(BigInteger.valueOf(4), Money.roundHalfEven(BigInteger.valueOf(7), BigInteger.TWO));
        assertEquals(BigInteger.valueOf(-4), Money.roundHalfEven(BigInteger.valueOf(-7), BigInteger.TWO));
    }

    @Test
    void allocationKeepsEveryMinorUnit() {
        long[] parts = Money.allocate(1_001, "USD", new long[] {3, 3, 3});
        assertArrayEquals(new long[] {334, 334, 333}, parts);
        assertEquals(1_001, parts[0] + parts[1] + parts[2]);
    }

    @Test
    void errorsCarryTheSpecCode() {
        assertEquals(
                "overflow",
                assertThrows(SpecException.class, () -> Money.add(Money.MAX_MINOR, 1, "USD"))
                        .code());
        assertEquals(
                "unknown_currency",
                assertThrows(SpecException.class, () -> Money.scale("ABC")).code());
        assertEquals("error:unknown_operation", Evaluate.run("divide", List.of("1", "2")));
    }

    @Test
    void splitCrossesTheYearEnd() {
        assertEquals(2, DateRanges.splitByMonth("2024-12-31", "2025-01-02").size());
    }
}
