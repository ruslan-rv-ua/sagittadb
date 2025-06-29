#!/usr/bin/env python3
"""Simple test runner script for SagittaDB."""

import subprocess
import sys
from pathlib import Path


def run_tests():
    """Run the test suite with different configurations."""
    test_dir = Path(__file__).parent

    print("🧪 Running SagittaDB Test Suite")
    print("=" * 50)

    # Basic test run
    print("\n📋 Running all tests...")
    result = subprocess.run(
        [sys.executable, "-m", "pytest", str(test_dir), "-v", "--tb=short"],
        cwd=test_dir.parent,
    )

    if result.returncode != 0:
        print("❌ Tests failed!")
        return result.returncode

    print("✅ All tests passed!")

    # Run with coverage if pytest-cov is available
    print("\n📊 Running tests with coverage...")
    try:
        coverage_result = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                str(test_dir),
                "--cov=sagittadb",
                "--cov-report=term-missing",
            ],
            cwd=test_dir.parent,
        )

        if coverage_result.returncode == 0:
            print("✅ Coverage report generated!")
        else:
            print("⚠️  Coverage report failed (pytest-cov might not be installed)")
    except FileNotFoundError:
        print("⚠️  pytest-cov not available, skipping coverage")

    # Run performance tests separately
    print("\n⚡ Running performance tests...")
    perf_result = subprocess.run(
        [sys.executable, "-m", "pytest", str(test_dir), "-m", "slow", "-v"],
        cwd=test_dir.parent,
    )

    if perf_result.returncode == 0:
        print("✅ Performance tests passed!")
    else:
        print("⚠️  Some performance tests failed or took too long")

    return 0


if __name__ == "__main__":
    sys.exit(run_tests())
