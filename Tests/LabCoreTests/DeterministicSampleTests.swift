import XCTest
@testable import LabCore

final class DeterministicSampleTests: XCTestCase {
    func testMedianOfOddSample() {
        XCTAssertEqual(DeterministicSample.median([11, 3, 7]), 7)
    }

    func testMedianOfEvenSample() {
        XCTAssertEqual(DeterministicSample.median([4, 10, 2, 8]), 6)
    }

    func testEmptySampleHasNoMedian() {
        XCTAssertNil(DeterministicSample.median([]))
    }

    func testSafeSum() {
        XCTAssertEqual(DeterministicSample.safeSum([4, -2, 8]), 10)
        XCTAssertNil(DeterministicSample.safeSum([Int.max, 1]))
    }

    func testActorIsDeterministic() async {
        let counter = TestCounter()
        let first = await counter.increment()
        let second = await counter.increment()
        let total = await counter.currentValue()
        XCTAssertEqual([first, second, total], [1, 2, 2])
    }
}
