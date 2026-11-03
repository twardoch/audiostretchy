#!/usr/bin/env python3
# this_file: scripts/compile_c.py
"""
Standalone C library compilation script.
Handles cross-platform compilation of the audio-stretch library.
"""

import argparse
import sys
from pathlib import Path


def main():
    """Main compilation script."""
    parser = argparse.ArgumentParser(description="Compile audio-stretch C library")
    parser.add_argument("--force", action="store_true", help="Force recompilation")
    parser.add_argument("--clean", action="store_true", help="Clean compiled libraries")
    parser.add_argument(
        "--source-dir", type=Path, help="Audio-stretch source directory"
    )
    parser.add_argument(
        "--output-dir", type=Path, help="Output directory for libraries"
    )
    parser.add_argument("--verbose", action="store_true", help="Verbose output")

    args = parser.parse_args()

    # Add project src to path
    project_root = Path(__file__).parent.parent
    sys.path.insert(0, str(project_root / "src"))

    from audiostretchy.c_interface.build import AudioStretchBuilder

    # Create builder
    builder = AudioStretchBuilder(args.source_dir, args.output_dir)

    if args.verbose:
        print(f"Source directory: {builder.source_dir}")
        print(f"Output directory: {builder.output_dir}")
        print(f"Platform: {builder.system} ({builder.arch})")

    # Perform requested action
    if args.clean:
        builder.clean()
    else:
        lib_path = builder.compile_library(force=args.force)
        print(f"Compiled library: {lib_path}")


if __name__ == "__main__":
    main()
