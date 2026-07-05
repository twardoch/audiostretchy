# this_file: src/audiostretchy/__init__.py
"""
AudioStretchy - High-quality audio time-stretching without pitch modification.

AudioStretchy uses David Bryant's audio-stretch C library with Pedalboard
for versatile audio I/O to provide fast, high-quality time-stretching
of audio files without changing their pitch.
"""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("audiostretchy")
except PackageNotFoundError:
    __version__ = "unknown"
finally:
    del version, PackageNotFoundError

from .core import AudioStretch, stretch_audio

__all__ = ["AudioStretch", "__version__", "stretch_audio"]
