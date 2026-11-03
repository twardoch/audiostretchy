# this_file: tests/test_build.py
"""Verify the native build path and failures before producing distributions."""

import pytest

from audiostretchy.c_interface.build import AudioStretchBuilder
from audiostretchy.c_interface.wrapper import TDHSAudioStretch


def test_builder_compiles_bundled_source_and_loads_exports(tmp_path):
    import ctypes

    builder = AudioStretchBuilder(output_dir=tmp_path)
    output = builder.compile_library(force=True)
    assert output.name in {"_stretch.so", "_stretch.dylib", "_stretch.dll"}
    library = ctypes.CDLL(str(output))
    for name in ("init", "output_capacity", "samples", "flush", "reset", "deinit"):
        assert getattr(library, f"stretch_{name}"), f"Missing native export {name}"
    assert builder.compile_library() == output


def test_builder_reports_missing_source(tmp_path):
    with pytest.raises(FileNotFoundError, match=r"stretch\.c"):
        AudioStretchBuilder(source_dir=tmp_path).compile_library()


def test_native_context_rejects_invalid_periods_without_crashing():
    with pytest.raises(ValueError, match="period"):
        TDHSAudioStretch(0, 100, 1, 0)


def test_native_context_can_be_closed_twice():
    context = TDHSAudioStretch(100, 800, 1, 0)
    context.reset()
    context.deinit()
    context.deinit()
    assert context.handle is None


@pytest.mark.parametrize("ratio", [float("nan"), float("inf"), 0.1, 5.0])
def test_stretch_rejects_ratios_outside_native_range(ratio):
    import numpy as np

    from audiostretchy import AudioStretch

    audio = AudioStretch()
    audio.samples = np.zeros((1, 1000), dtype=np.float32)
    with pytest.raises(ValueError, match="ratio"):
        audio.stretch(ratio)
