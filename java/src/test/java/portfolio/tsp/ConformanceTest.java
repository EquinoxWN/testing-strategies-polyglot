package portfolio.tsp;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Arrays;
import java.util.List;
import java.util.stream.Stream;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.params.ParameterizedTest;
import org.junit.jupiter.params.provider.Arguments;
import org.junit.jupiter.params.provider.MethodSource;

/** Every row of the shared specification, spec/vectors.tsv, must give exactly the expected answer. */
class ConformanceTest {
    static final Path VECTORS = Path.of("..", "spec", "vectors.tsv");

    /** The vector rows: id, expected, operation, arguments. */
    static Stream<Arguments> vectors() throws IOException {
        return Files.readAllLines(VECTORS, StandardCharsets.UTF_8).stream()
                .filter(l -> !l.isBlank() && !l.startsWith("#"))
                .map(l -> Arrays.asList(l.split("\t", -1)))
                .map(c -> Arguments.of(c.get(0), c.get(1), c.get(2), c.subList(3, c.size())));
    }

    @ParameterizedTest(name = "{0}: {2} {3} -> {1}")
    @MethodSource("vectors")
    void matchesTheSpec(String id, String expected, String op, List<String> args) {
        assertEquals(expected, Evaluate.run(op, args), id);
    }

    @Test
    void theSpecIsNotEmpty() throws IOException {
        assertTrue(vectors().count() >= 70);
    }
}
