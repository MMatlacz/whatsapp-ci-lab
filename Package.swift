// swift-tools-version: 6.0
import PackageDescription

let package = Package(
    name: "SyntheticXcodeCILab",
    platforms: [.macOS(.v14), .iOS(.v17)],
    products: [
        .library(name: "LabCore", targets: ["LabCore"])
    ],
    targets: [
        .target(name: "LabCore"),
        .testTarget(name: "LabCoreTests", dependencies: ["LabCore"])
    ]
)
