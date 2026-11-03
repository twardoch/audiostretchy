#!/usr/bin/env python3
# this_file: scripts/build_local.py
"""
Local build script for AudioStretchy.
Compiles C library and builds Python wheels for local development.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path


def setup_environment():
    """Set up the build environment."""
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)


def compile_c_library(force: bool = False):
    """Compile the audio-stretch C library."""
    print("Compiling C library...")

    # Import and use the build utility
    sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
    from audiostretchy.c_interface.build import AudioStretchBuilder

    builder = AudioStretchBuilder()
    lib_path = builder.compile_library(force=force)
    print(f"C library compiled: {lib_path}")

    return lib_path


def build_wheel():
    """Build Python wheel using hatch."""
    print("Building Python wheel...")

    try:
        result = subprocess.run(
            ["uv", "build"], capture_output=True, text=True, check=True
        )
        print("Wheel build successful!")
        if result.stdout:
            print(result.stdout)

    except subprocess.CalledProcessError as e:
        print(f"Wheel build failed: {e}")
        if e.stdout:
            print("stdout:", e.stdout)
        if e.stderr:
            print("stderr:", e.stderr)
        raise


def install_dev_dependencies():
    """Install development dependencies."""
    print("Installing development dependencies...")

    try:
        subprocess.run(["uv", "sync"], check=True)
        print("Development dependencies installed!")

    except subprocess.CalledProcessError as e:
        print(f"Failed to install dependencies: {e}")
        raise


def run_tests():
    """Run the test suite."""
    print("Running tests...")

    try:
        subprocess.run(["uv", "run", "pytest", "tests/", "-v"], check=True)
        print("All tests passed!")

    except subprocess.CalledProcessError as e:
        print(f"Tests failed: {e}")
        raise


def main():
    """Main build script."""
    parser = argparse.ArgumentParser(description="Local build script for AudioStretchy")
    parser.add_argument(
        "--force", action="store_true", help="Force rebuild of C library"
    )
    parser.add_argument(
        "--no-compile", action="store_true", help="Skip C library compilation"
    )
    parser.add_argument("--no-wheel", action="store_true", help="Skip wheel building")
    parser.add_argument(
        "--no-install", action="store_true", help="Skip dev dependency installation"
    )
    parser.add_argument("--test", action="store_true", help="Run tests after building")

    args = parser.parse_args()

    print("=== AudioStretchy Local Build ===")

    # Set up environment
    setup_environment()

    # Compile C library
    if not args.no_compile:
        compile_c_library(force=args.force)

    # Install dev dependencies
    if not args.no_install:
        install_dev_dependencies()

    # Build wheel
    if not args.no_wheel:
        build_wheel()

    # Run tests if requested
    if args.test:
        run_tests()

    print("=== Build Complete ===")


if __name__ == "__main__":
    main()
