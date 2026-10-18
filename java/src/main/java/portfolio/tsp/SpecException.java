package portfolio.tsp;

/** A specification error; the code is shared by the Java, Python and JavaScript implementations. */
public final class SpecException extends RuntimeException {
    private static final long serialVersionUID = 1L;

    private final String code;

    /** Creates the error with its spec code, e.g. {@code overflow}. */
    public SpecException(String code) {
        super(code, null, false, false);
        this.code = code;
    }

    /** The spec code. */
    public String code() {
        return code;
    }
}
