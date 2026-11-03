# this_file: hatch_build.py
"""Build TDHS once per platform; ctypes needs no CPython ABI tag."""

import os
import platform
import runpy
from pathlib import Path

from hatchling.builders.hooks.plugin.interface import BuildHookInterface
from packaging.tags import sys_tags


class NativeBuildHook(BuildHookInterface):
    def initialize(self, version: str, build_data: dict) -> None:
        package = Path(self.root) / "src" / "audiostretchy"
        builder = runpy.run_path(str(package / "c_interface" / "build.py"))[
            "AudioStretchBuilder"
        ]
        output = builder().compile_library(force=True)
        build_data["pure_python"] = False
        platform_tag = next(sys_tags()).platform
        if platform.system() == "Darwin":
            target = os.environ.get("MACOSX_DEPLOYMENT_TARGET", "11.0")
            platform_tag = f"macosx_{target.replace('.', '_')}_{platform.machine()}"
        build_data["tag"] = f"py3-none-{platform_tag}"
        build_data["force_include"][str(output)] = (
            f"audiostretchy/c_interface/lib/{output.name}"
        )
