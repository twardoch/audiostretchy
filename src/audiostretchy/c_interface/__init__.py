# this_file: src/audiostretchy/c_interface/__init__.py
"""
C interface module for AudioStretchy.
Provides access to the compiled audio-stretch C library.
"""

from .wrapper import TDHSAudioStretch

__all__ = ["TDHSAudioStretch"]
