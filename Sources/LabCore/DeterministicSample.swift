/// Deliberately synthetic and independent of any private application source.
/// These small algorithms exercise Swift compilation and XCTest on CI runners.
public enum DeterministicSample {
    /// The median of a nonempty integer sample, or nil for no observations.
    public static func median(_ values: [Int]) -> Double? {
        guard !values.isEmpty else { return nil }
        let ordered = values.sorted()
        let center = ordered.count / 2
        if ordered.count % 2 == 1 {
            return Double(ordered[center])
        }
        // Convert before averaging so Int arithmetic cannot overflow.
        return Double(ordered[center - 1]) / 2 + Double(ordered[center]) / 2
    }

    /// Add values only when the exact result fits in an Int.
    public static func safeSum(_ values: [Int]) -> Int? {
        var result = 0
        for value in values {
            let next = result.addingReportingOverflow(value)
            guard !next.overflow else { return nil }
            result = next.partialValue
        }
        return result
    }
}

/// A tiny synthetic actor to exercise Swift 6 concurrency compilation.
public actor TestCounter {
    private var value = 0

    public init() {}

    @discardableResult
    public func increment() -> Int {
        value += 1
        return value
    }

    public func currentValue() -> Int { value }
}
