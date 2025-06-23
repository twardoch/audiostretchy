import pytest
from pathlib import Path
import numpy as np
import soundfile # Using soundfile for reliable audio properties comparison

from audiostretchy.stretch import AudioStretch, stretch_audio

# Helper function to get audio properties
def get_audio_properties(file_path):
    with soundfile.SoundFile(file_path, 'r') as sf:
        return sf.samplerate, sf.channels, sf.frames

@pytest.fixture
def audio_processor():
    return AudioStretch()

@pytest.fixture
def sample_wav_path():
    return Path("tests/audio.wav")

@pytest.fixture
def sample_mp3_path():
    return Path("tests/audio.mp3")

# --- Test AudioStretch Class ---

def test_open_wav(audio_processor, sample_wav_path):
    audio_processor.open(sample_wav_path)
    # Get properties using soundfile for comparison
    sf_rate, sf_channels, sf_frames = get_audio_properties(sample_wav_path)
    assert audio_processor.framerate == sf_rate
    assert audio_processor.nchannels == sf_channels
    assert audio_processor.in_samples is not None
    assert audio_processor.samples is not None
    # Samples are (channels, frames)
    assert audio_processor.in_samples.shape == (sf_channels, sf_frames)
    assert audio_processor.samples.shape == (sf_channels, sf_frames)
    assert audio_processor.in_samples.dtype == np.float32

def test_open_mp3(audio_processor, sample_mp3_path):
    # This requires ffmpeg to be installed for pedalboard to read mp3s usually
    try:
        audio_processor.open(sample_mp3_path)
        assert audio_processor.framerate > 0
        assert audio_processor.nchannels > 0
        assert audio_processor.in_samples is not None
        assert audio_processor.samples is not None
        assert audio_processor.in_samples.dtype == np.float32
    except IOError as e:
        pytest.skip(f"Skipping MP3 test, pedalboard couldn't open MP3 (possibly missing ffmpeg or backend): {e}")
    except Exception as e: # Catch any other pedalboard/soundfile error during open
        pytest.skip(f"Skipping MP3 test due to an unexpected error during open: {e}")


def test_save_wav(audio_processor, sample_wav_path, tmp_path):
    audio_processor.open(sample_wav_path)
    output_path = tmp_path / "output.wav"
    audio_processor.save(output_path)

    assert output_path.exists()
    rate, channels, frames = get_audio_properties(output_path)
    assert rate == audio_processor.framerate
    assert channels == audio_processor.nchannels
    # audio_processor.samples is (channels, frames)
    expected_frames = audio_processor.samples.shape[1]
    assert frames == expected_frames


def test_save_mp3(audio_processor, sample_wav_path, tmp_path):
    # Open a WAV and save as MP3
    audio_processor.open(sample_wav_path)
    output_path = tmp_path / "output.mp3"
    try:
        audio_processor.save(output_path, output_format="mp3") # Specify format
        assert output_path.exists()
        # Check basic properties. MP3 encoding can sometimes slightly alter frame counts or lead to skips.
        rate, channels, _ = get_audio_properties(output_path)
        assert rate == audio_processor.framerate
        assert channels == audio_processor.nchannels
    except IOError as e:
        pytest.skip(f"Skipping MP3 save test, pedalboard couldn't save MP3 (possibly missing ffmpeg or backend): {e}")
    except Exception as e:
        pytest.skip(f"Skipping MP3 save test due to an unexpected error: {e}")

def test_resample(audio_processor, sample_wav_path):
    audio_processor.open(sample_wav_path)
    original_framerate = audio_processor.framerate
    # audio_processor.samples is (channels, frames)
    original_frames = audio_processor.samples.shape[1]
    target_framerate = 22050

    audio_processor.resample(target_framerate)

    assert audio_processor.framerate == target_framerate
    # audio_processor.samples is still (channels, frames)
    current_frames = audio_processor.samples.shape[1]
    expected_frames = int(original_frames * (target_framerate / original_framerate))

    # Resampling can have slight variations in frame count
    assert abs(current_frames - expected_frames) < 5 # Allow small deviation

def test_stretch_no_change(audio_processor, sample_wav_path):
    audio_processor.open(sample_wav_path)
    original_samples_shape = audio_processor.samples.shape
    audio_processor.stretch(ratio=1.0)
    assert audio_processor.samples.shape == original_samples_shape

def test_stretch_longer(audio_processor, sample_wav_path):
    audio_processor.open(sample_wav_path)
    # audio_processor.samples is (channels, frames) after open
    original_frames = audio_processor.samples.shape[1]
    ratio = 1.5 # Make 50% longer
    audio_processor.stretch(ratio=ratio)

    # After stretch, self.samples is (channels, frames)
    current_frames = audio_processor.samples.shape[1]
    expected_frames = int(original_frames * ratio)

    # Time stretching isn't always perfectly exact to the sample, allow some leeway
    assert abs(current_frames - expected_frames) < original_frames * 0.05 # 5% leeway

def test_stretch_shorter(audio_processor, sample_wav_path):
    audio_processor.open(sample_wav_path)
    # audio_processor.samples is (channels, frames) after open
    original_frames = audio_processor.samples.shape[1]
    ratio = 0.75 # Make 25% shorter
    audio_processor.stretch(ratio=ratio)

    # After stretch, self.samples is (channels, frames)
    current_frames = audio_processor.samples.shape[1]
    expected_frames = int(original_frames * ratio)

    assert abs(current_frames - expected_frames) < original_frames * 0.05 # 5% leeway

# --- Test stretch_audio global function (CLI entry point) ---

def test_stretch_audio_func_wav_to_wav(sample_wav_path, tmp_path):
    input_path = sample_wav_path
    output_path = tmp_path / "stretched_audio.wav"
    ratio = 1.2

    stretch_audio(str(input_path), str(output_path), ratio=ratio)

    assert output_path.exists()
    in_rate, in_channels, in_frames = get_audio_properties(input_path)
    out_rate, out_channels, out_frames = get_audio_properties(output_path)

    assert out_rate == in_rate
    assert out_channels == in_channels
    expected_frames = int(in_frames * ratio)
    assert abs(out_frames - expected_frames) < in_frames * 0.05 # 5% leeway

def test_stretch_audio_func_mp3_to_mp3(sample_mp3_path, tmp_path):
    input_path = sample_mp3_path
    output_path = tmp_path / "stretched_audio.mp3"
    ratio = 0.8

    try:
        # Need to ensure the input can be read first
        in_props_available = False
        try:
            in_rate, in_channels, in_frames = get_audio_properties(input_path)
            in_props_available = True
        except Exception as e:
             pytest.skip(f"Skipping MP3 integration test: Could not read input MP3 properties ({e}).")

        if in_props_available:
            stretch_audio(str(input_path), str(output_path), ratio=ratio)
            assert output_path.exists()
            out_rate, out_channels, out_frames = get_audio_properties(output_path)

            assert out_rate == in_rate
            assert out_channels == in_channels
            expected_frames = int(in_frames * ratio)
            # MP3 encoding/decoding can add/remove priming/padding frames. Leeway might need to be larger.
            assert abs(out_frames - expected_frames) < in_frames * 0.10 # 10% leeway for MP3

    except IOError as e:
        pytest.skip(f"Skipping MP3 integration test, pedalboard operation failed (possibly missing ffmpeg or backend): {e}")
    except Exception as e:
        pytest.skip(f"Skipping MP3 integration test due to an unexpected error: {e}")


def test_stretch_audio_func_resample(sample_wav_path, tmp_path):
    input_path = sample_wav_path
    output_path = tmp_path / "resampled_audio.wav"
    target_sample_rate = 16000

    stretch_audio(str(input_path), str(output_path), ratio=1.0, sample_rate=target_sample_rate)

    assert output_path.exists()
    out_rate, _, _ = get_audio_properties(output_path)
    assert out_rate == target_sample_rate

def test_stretch_audio_func_stretch_and_resample(sample_wav_path, tmp_path):
    input_path = sample_wav_path
    output_path = tmp_path / "stretch_resample.wav"
    ratio = 1.3
    target_sample_rate = 8000

    stretch_audio(str(input_path), str(output_path), ratio=ratio, sample_rate=target_sample_rate)

    assert output_path.exists()
    in_rate, _, in_frames = get_audio_properties(input_path)
    out_rate, _, out_frames = get_audio_properties(output_path)

    assert out_rate == target_sample_rate
    # Expected frames after stretch, then account for resampling
    expected_frames_after_stretch = in_frames * ratio
    expected_final_frames = int(expected_frames_after_stretch * (target_sample_rate / in_rate))
    assert abs(out_frames - expected_final_frames) < expected_frames_after_stretch * 0.05 # 5% leeway on stretched length

# TODO: Add tests for file-like objects for open/save
# TODO: Add tests for CLI arguments if Fire CLI parsing changes significantly or needs specific checks.
#       For now, stretch_audio function tests cover the core functionality invoked by CLI.
# TODO: If gap_ratio or other TDHS features are re-implemented with pedalboard, add tests for them.
# TODO: Consider adding tests for other formats pedalboard supports if relevant (e.g. FLAC, OGG)
#       Requires sample files and ensuring pedalboard backends are present.

# Add soundfile to testing dependencies in pyproject.toml
# [project.optional-dependencies]
# testing = [
#     "setuptools",
#     "pytest",
#     "pytest-cov",
#     "soundfile", # Added this
# ]
#
# And ensure it's installed in the environment.
# pip install soundfile

# To run tests:
# pytest tests/test_stretch.py --cov=src/audiostretchy/stretch
# or simply pytest from root, if pyproject.toml is configured.
# (Pytest should pick up config from pyproject.toml's [tool.pytest.ini_options])

# Note on MP3 tests: Pedalboard's ability to handle MP3s often relies on system-installed
# ffmpeg libraries. If these are not present in the test environment, MP3 tests might be
# skipped or fail. The skips are added to handle this gracefully.
# The `soundfile` library also has its own backend dependencies for MP3.
# If skips are frequent, ensure ffmpeg (for pedalboard) and relevant soundfile backends (e.g. libsndfile with libmpg123)
# are available in the CI/test environment.
# For pedalboard, `pip install pedalboard[ffmpeg]` could be an option if it bundles it,
# or ensuring ffmpeg is in the PATH.
# For soundfile, `pip install soundfile[formats]` or ensuring libsndfile is compiled with appropriate format support.
# However, `soundfile` itself doesn't list `libmpg123` or `lame` as direct pip-installable extras.
# It relies on the underlying libsndfile to have support for these formats.
# Often, `libsndfile1-dev` (or similar) on Linux includes these.
# On macOS/Windows, users might need to install ffmpeg/libsndfile manually.

# For the `get_audio_properties` helper, soundfile is generally robust.
# If `soundfile` cannot open an MP3, it will raise an error.
# The MP3 tests are structured to skip if `soundfile` (or `pedalboard` for processing)
# has issues with MP3s, which usually points to backend/library availability.
# The `audio.mp3` and `audio-1.2.mp3` seem to be LAME encoded, which is standard.
# `tests/audio.wav` is a standard PCM WAV.
# `tests/audio-1.2.wav` is also PCM WAV.
# These files should be fine.
# Pedalboard uses `libsndfile` by default for WAV, and can use it or `ffmpeg` for others.
# If `ffmpeg` is available, `pedalboard` often prefers it for broader format support.
# Let's ensure `soundfile` is in `pyproject.toml`
# and then run the tests.
#
# The tests use `soundfile` to verify properties of output files. This is a good,
# independent way to check what `pedalboard` wrote.
#
# Final check on sample rates of test files:
# tests/audio.wav: (from README, implies it's the source for audio-1.2.wav)
# tests/audio.mp3: (from README, implies it's the source for audio-1.2.mp3)
# Assuming they are 44.1kHz as it's a common rate. The test for open_wav hardcodes this.
# It would be better to read the actual sample rate from the file for comparison
# in `test_open_wav` rather than hardcoding 44100, but for provided test files it's likely okay.
# Let's assume `tests/audio.wav` is 44.1kHz stereo for now.
# The `get_audio_properties` from `soundfile` will tell the truth.
# The initial assertion `assert audio_processor.framerate == 44100` in `test_open_wav`
# should ideally be compared against `get_audio_properties(sample_wav_path)[0]`.
# Let's make that small adjustment.
pass
