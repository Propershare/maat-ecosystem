// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "MAAT-App",
    platforms: [.iOS(.v17)],
    products: [
        .library(name: "MAAT-App", targets: ["MAAT-App"]),
    ],
    dependencies: [
        // MLX Swift for on-device Gemma 4
        .package(url: "https://github.com/ml-explore/mlx-swift", branch: "main"),
        // Meta glasses SDK placeholder
    ],
    targets: [
        .target(
            name: "MAAT-App",
            dependencies: [
                .product(name: "MLX", package: "mlx-swift"),
                .product(name: "MLXNN", package: "mlx-swift"),
                .product(name: "MLXOptimizers", package: "mlx-swift"),
            ],
            resources: [
                .process("Resources")
            ]
        ),
        .testTarget(
            name: "MAAT-AppTests",
            dependencies: ["MAAT-App"]
        ),
    ]
)
