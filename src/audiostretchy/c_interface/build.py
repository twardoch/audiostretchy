# this_file: src/audiostretchy/c_interface/build.py
"""Compile the bundled TDHS source for the build host; no network required."""

import os
import platform
import shlex
import subprocess
from pathlib import Path

EXPORTS = ("init", "output_capacity", "samples", "flush", "reset", "deinit")


class AudioStretchBuilder:
    """Shared native compiler used by Hatch and the development helper."""

    def __init__(self, source_dir: Path | None = None, output_dir: Path | None = None):
        package = Path(__file__).resolve().parent.parent
        self.source_dir = source_dir or package / "_vendor" / "audio-stretch"
        self.output_dir = output_dir or package / "c_interface" / "lib"
        self.system = platform.system()
        self.arch = platform.machine().lower()

    def compile_library(self, force: bool = False) -> Path:
        """Compile one shared library, or reuse a newer development build."""
        source = self.source_dir / "stretch.c"
        header = self.source_dir / "stretch.h"
        if not source.is_file() or not header.is_file():
            raise FileNotFoundError(
                f"stretch.c and stretch.h required in {self.source_dir}"
            )
        extensions = {"Windows": ".dll", "Darwin": ".dylib", "Linux": ".so"}
        if self.system not in extensions:
            raise RuntimeError(f"Unsupported platform: {self.system}")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        output = (self.output_dir / ("_stretch" + extensions[self.system])).resolve()
        if (
            not force
            and output.exists()
            and output.stat().st_mtime
            > max(source.stat().st_mtime, header.stat().st_mtime)
        ):
            return output
        compiler = shlex.split(
            os.environ.get("CC", "cl" if self.system == "Windows" else "cc")
        )
        if self.system == "Windows":
            command = [
                *compiler,
                "/nologo",
                "/O2",
                "/LD",
                "/MT",
                str(source.resolve()),
                f"/Fe:{output}",
                "/link",
                *[f"/EXPORT:stretch_{name}" for name in EXPORTS],
            ]
        else:
            deployment = (
                [
                    f"-mmacosx-version-min={os.environ.get('MACOSX_DEPLOYMENT_TARGET', '11.0')}"
                ]
                if self.system == "Darwin"
                else []
            )
            command = [
                *compiler,
                "-O3",
                "-fPIC",
                "-dynamiclib" if self.system == "Darwin" else "-shared",
                *(
                    ["-Wl,-install_name,@rpath/_stretch.dylib"]
                    if self.system == "Darwin"
                    else []
                ),
                *deployment,
                *shlex.split(os.environ.get("CFLAGS", "")),
                str(source.resolve()),
                "-o",
                str(output),
                *shlex.split(os.environ.get("LDFLAGS", "")),
                "-lm",
            ]
        subprocess.run(command, cwd=self.output_dir, check=True)
        return output

    def clean(self) -> None:
        """Delete only generated native build products."""
        for pattern in ("_stretch.*", "stretch.obj"):
            for path in self.output_dir.glob(pattern):
                path.unlink()
