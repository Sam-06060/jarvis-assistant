// swift-tools-version:5.5
import PackageDescription

let package = Package(
    name: "JarvisApp",
    platforms: [
        .macOS("13.0")
    ],
    products: [
        .executable(name: "JarvisApp", targets: ["JarvisApp"])
    ],
    dependencies: [],
    targets: [
        .executableTarget(
            name: "JarvisApp",
            dependencies: [],
            path: "Sources",
            exclude: [],
            resources: [
                .copy("Resources")
            ]
        )
    ]
)
