"""
Test configuration and fixtures for audiostretchy.

This file contains shared fixtures and test utilities for the audiostretchy test suite.
"""

import shutil
import tempfile
from pathlib import Path

import numpy as np
import pytest
import soundfile as sf


@pytest.fixture(scope="session")
def temp_audio_dir():
    """Create a temporary directory for test audio files."""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture(scope="session")
def sample_audio_generator():
    """Generate sample audio data for testing."""

    def generate_audio(
        duration_seconds=1.0, sample_rate=44100, channels=2, frequency=440.0
    ):
        """Generate a sine wave audio sample."""
        num_samples = int(duration_seconds * sample_rate)
        t = np.linspace(0, duration_seconds, num_samples, False)

        # Generate sine wave
        audio = np.sin(2 * np.pi * frequency * t)

        # Convert to stereo if needed
        if channels == 2:
            audio = np.stack([audio, audio])
        elif channels == 1:
            audio = audio.reshape(1, -1)

        return audio.astype(np.float32)

    return generate_audio


@pytest.fixture(scope="session")
def generate_test_files(temp_audio_dir, sample_audio_generator):
    """Generate test audio files in various formats."""
    test_files = {}

    # Generate mono and stereo audio
    mono_audio = sample_audio_generator(channels=1)
    stereo_audio = sample_audio_generator(channels=2)

    # Create WAV files
    mono_wav = temp_audio_dir / "mono_test.wav"
    stereo_wav = temp_audio_dir / "stereo_test.wav"

    sf.write(mono_wav, mono_audio.T, 44100)
    sf.write(stereo_wav, stereo_audio.T, 44100)

    test_files["mono_wav"] = mono_wav
    test_files["stereo_wav"] = stereo_wav

    # Generate audio with silence (for gap_ratio testing)
    silent_audio = sample_audio_generator(duration_seconds=0.5, frequency=0)  # silence
    normal_audio = sample_audio_generator(duration_seconds=0.5, frequency=440)  # tone

    # Concatenate: tone -> silence -> tone
    gapped_audio = np.concatenate([normal_audio, silent_audio, normal_audio], axis=1)
    gapped_wav = temp_audio_dir / "gapped_test.wav"
    sf.write(gapped_wav, gapped_audio.T, 44100)
    test_files["gapped_wav"] = gapped_wav

    return test_files


@pytest.fixture
def audio_properties_checker():
    """Fixture to check audio file properties."""

    def check_properties(file_path):
        with sf.SoundFile(file_path, "r") as audio_file:
            return {
                "sample_rate": audio_file.samplerate,
                "channels": audio_file.channels,
                "frames": audio_file.frames,
                "duration": audio_file.frames / audio_file.samplerate,
            }

    return check_properties


@pytest.fixture
def tolerance_checker():
    """Fixture for checking numeric tolerances in tests."""

    def check_tolerance(actual, expected, tolerance_percent=5):
        """Check if actual value is within tolerance_percent of expected."""
        tolerance = abs(expected * tolerance_percent / 100)
        return abs(actual - expected) <= tolerance

    return check_tolerance
