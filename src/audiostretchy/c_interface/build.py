# this_file: src/audiostretchy/c_interface/build.py
"""
Build utilities for compiling the audio-stretch C library.
Handles cross-platform compilation and library placement.
"""

import platform
import shutil
import subprocess
from pathlib import Path


class AudioStretchBuilder:
    """Handles compilation of the audio-stretch C library."""

    def __init__(self, source_dir: Path | None = None, output_dir: Path | None = None):
        """
        Initialize the builder.

        Args:
            source_dir: Path to audio-stretch source code (defaults to project submodule)
            output_dir: Path for compiled libraries (defaults to c_interface/lib)
        """
        self.project_root = Path(__file__).parent.parent.parent.parent
        self.source_dir = source_dir or self.project_root / "audio-stretch"
        self.output_dir = output_dir or Path(__file__).parent / "lib"

        self.system = platform.system()
        self.arch = platform.machine().lower()

    def get_compiler_config(self) -> dict[str, list[str]]:
        """Get compiler configuration for the current platform."""
        configs = {
            "Windows": {
                "compiler": ["cl.exe"],
                "flags": ["/O2", "/LD", "/MT"],
                "output_flag": "/Fe:",
                "extension": ".dll",
                "arch_suffix": "_x64" if self.arch in ("amd64", "x86_64") else "",
            },
            "Darwin": {  # macOS
                "compiler": ["clang"],
                "flags": ["-O3", "-shared", "-fPIC"],
                "output_flag": "-o",
                "extension": ".dylib",
                "arch_suffix": "_arm64"
                if self.arch in ("arm64", "aarch64")
                else "_x64",
            },
            "Linux": {
                "compiler": ["gcc"],
                "flags": ["-O3", "-shared", "-fPIC"],
                "output_flag": "-o",
                "extension": ".so",
                "arch_suffix": "_aarch64"
                if self.arch in ("aarch64", "arm64")
                else "_x64",
            },
        }

        if self.system not in configs:
            raise RuntimeError(f"Unsupported platform: {self.system}")

        return configs[self.system]

    def find_source_files(self) -> list[Path]:
        """Find C source files to compile."""
        source_files = []

        stretch_c = self.source_dir / "stretch.c"
        if stretch_c.exists():
            source_files.append(stretch_c)
        else:
            raise FileNotFoundError(f"stretch.c not found in {self.source_dir}")

        return source_files

    def compile_library(self, force: bool = False) -> Path:
        """
        Compile the audio-stretch library.

        Args:
            force: Force recompilation even if library exists

        Returns:
            Path to the compiled library
        """
        config = self.get_compiler_config()

        # Determine output filename
        lib_name = f"_stretch{config['arch_suffix']}{config['extension']}"
        output_path = self.output_dir / lib_name

        # Check if compilation is needed
        if not force and output_path.exists():
            source_files = self.find_source_files()
            if all(
                output_path.stat().st_mtime > src.stat().st_mtime
                for src in source_files
            ):
                print(f"Library {lib_name} is up to date")
                return output_path

        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Find source files
        source_files = self.find_source_files()

        # Build command
        cmd = config["compiler"].copy()
        cmd.extend(config["flags"])
        cmd.extend([str(f) for f in source_files])

        if config["output_flag"].endswith(":"):
            cmd.append(f"{config['output_flag']}{output_path}")
        else:
            cmd.extend([config["output_flag"], str(output_path)])

        print(f"Compiling {lib_name}...")
        print(f"Command: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd, cwd=self.source_dir, capture_output=True, text=True, check=True
            )

            if result.stdout:
                print("Compiler output:", result.stdout)

        except subprocess.CalledProcessError as e:
            print(f"Compilation failed with return code {e.returncode}")
            print(f"stdout: {e.stdout}")
            print(f"stderr: {e.stderr}")
            raise RuntimeError(f"Failed to compile {lib_name}") from e

        if not output_path.exists():
            raise RuntimeError(
                f"Compilation succeeded but {output_path} was not created"
            )

        print(f"Successfully compiled {lib_name}")
        return output_path

    def clean(self) -> None:
        """Remove compiled libraries."""
        if self.output_dir.exists():
            shutil.rmtree(self.output_dir)
            print(f"Cleaned {self.output_dir}")

    def build_all_platforms(
        self, platforms: list[str] | None = None
    ) -> dict[str, Path]:
        """
        Build libraries for multiple platforms (for CI use).

        Args:
            platforms: List of platforms to build for (None = current platform only)

        Returns:
            Dict mapping platform names to compiled library paths
        """
        if platforms is None:
            platforms = [self.system]

        results = {}

        for platform_name in platforms:
            if platform_name == self.system:
                # Build for current platform
                lib_path = self.compile_library()
                results[platform_name] = lib_path
            else:
                print(f"Cross-compilation for {platform_name} not implemented")

        return results


def main():
    """Command-line interface for building the C library."""
    import argparse

    parser = argparse.ArgumentParser(description="Build audio-stretch C library")
    parser.add_argument("--force", action="store_true", help="Force recompilation")
    parser.add_argument("--clean", action="store_true", help="Clean compiled libraries")
    parser.add_argument(
        "--source-dir", type=Path, help="Audio-stretch source directory"
    )
    parser.add_argument(
        "--output-dir", type=Path, help="Output directory for libraries"
    )

    args = parser.parse_args()

    builder = AudioStretchBuilder(args.source_dir, args.output_dir)

    if args.clean:
        builder.clean()
    else:
        builder.compile_library(force=args.force)


if __name__ == "__main__":
    main()
