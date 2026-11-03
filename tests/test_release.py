# this_file: tests/test_release.py
"""A resumed release must upload only its downloaded artifacts, without tagging."""

import os
import shutil
import subprocess
from pathlib import Path

import pytest


@pytest.mark.skipif(os.name == "nt", reason="POSIX release entry point")
def test_resume_uploads_exact_release_files_without_new_tag(tmp_path):
    root = Path(__file__).resolve().parents[1]
    shutil.copy(root / "publish.sh", tmp_path / "publish.sh")
    binaries = tmp_path / "bin"
    binaries.mkdir()
    log = tmp_path / "commands"
    for name, body in {
        "gh": """case "$1 $2" in
'run list') echo 42;;
'release download') mkdir -p dist/v1.3.9; touch dist/v1.3.9/release.whl dist/v1.3.9/release.tar.gz;;
esac
""",
        "uvx": "",
        "uv": "",
        "git": "exit 99",
    }.items():
        executable = binaries / name
        executable.write_text(
            f'#!/bin/sh\necho "{name} $*" >> "$RELEASE_TEST_LOG"\n' + body
        )
        executable.chmod(0o755)
    stale = tmp_path / "dist" / "stale.whl"
    stale.parent.mkdir()
    stale.touch()
    result = subprocess.run(
        ["bash", "publish.sh", "--resume", "v1.3.9"],
        cwd=tmp_path,
        env={
            **os.environ,
            "PATH": f"{binaries}{os.pathsep}{os.environ['PATH']}",
            "RELEASE_TEST_LOG": str(log),
        },
        text=True,
        capture_output=True,
    )
    assert result.returncode == 0, result.stderr
    commands = log.read_text()
    assert "git " not in commands and "gitnextver" not in commands
    assert (
        "uv publish --check-url https://pypi.org/simple/ dist/v1.3.9/release.tar.gz dist/v1.3.9/release.whl"
        in commands
    )
    assert "stale.whl" not in commands
