# AudioStretchy

AudioStretchy is a Python library and CLI tool that performs high-quality time-stretching of audio files without changing their pitch. It is a Python wrapper around David Bryant’s excellent [audio-stretch C library](https://github.com/dbry/audio-stretch), which implements Time-Domain Harmonic Scaling (TDHS). AudioStretchy uses [Spotify's Pedalboard library](https://github.com/spotify/pedalboard) for robust audio file input/output (WAV, MP3, FLAC, OGG, etc.) and resampling.

_Version: (to be updated by release process)_

## Features

- **High-Quality Time Stretching**: Utilizes David Bryant's `audio-stretch` C library (TDHS algorithm), ideal for speech.
- **Silence-Aware Stretching**: Supports separate stretching ratios for gaps/silence in audio via the `gap_ratio` parameter (Note: current Python wrapper applies this if the C library has internal segmentation logic based on this, or if Python-side segmentation is added in future).
- **Broad Audio Format Support**: Reads and writes numerous audio formats (WAV, MP3, FLAC, OGG, etc.) using the Pedalboard library.
- **Resampling**: Supports audio resampling, also via Pedalboard.
- **Adjustable Parameters**: Fine-tune stretching with parameters like frequency limits for period detection, buffer sizes, and silence thresholds.
- **Cross-Platform**: Includes pre-compiled C libraries for Windows, macOS (x86_64, arm64), and Linux.
- **Simple CLI and Python API**.

**Time-Domain Harmonic Scaling (TDHS)** is a method for time-scale modification of speech (or other audio signals), allowing the apparent rate of speech articulation to be changed without affecting the pitch-contour and the time-evolution of the formant structure. TDHS differs from other time-scale modification algorithms in that time-scaling operations are performed in the time domain (not the frequency domain). The `audio-stretch` C library provides a high-quality TDHS implementation.

## Demo

Below are links to a short audio file (as WAV and MP3), with the same file stretched at 1.2 (20% slower):

| Input                                                                             | Stretched                                                                                 |
| --------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| [`audio.wav`](https://github.com/twardoch/audiostretchy/raw/main/tests/audio.wav) | [`audio-1.2.wav`](https://github.com/twardoch/audiostretchy/raw/main/tests/audio-1.2.wav) |
| [`audio.mp3`](https://github.com/twardoch/audiostretchy/raw/main/tests/audio.mp3) | [`audio-1.2.mp3`](https://github.com/twardoch/audiostretchy/raw/main/tests/audio-1.2.mp3) |


## Installation

AudioStretchy includes a C extension that provides the core TDHS algorithm. Pre-compiled wheels are provided for Windows, macOS, and Linux, so installation is typically straightforward:

```bash
python3 -m pip install audiostretchy
```
This command installs `audiostretchy` along with its dependencies:
- `numpy`: For numerical operations.
- `pedalboard`: For reading/writing various audio formats (WAV, MP3, FLAC, etc.) and for resampling.

**Note on Pedalboard Dependencies:** For `pedalboard` to support a wide range of audio formats, it might rely on system libraries like FFmpeg. If you encounter issues opening or saving specific file types (especially compressed ones like MP3), ensure FFmpeg is installed and accessible in your system's PATH.
- On **macOS**: `brew install ffmpeg`
- On **Linux (Debian/Ubuntu)**: `sudo apt-get install ffmpeg`
- On **Windows**: Download FFmpeg from the [official website](https://ffmpeg.org/download.html) and add its `bin` directory to your PATH.

### Development Installation

To install the development version from the repository:
```bash
git clone https://github.com/twardoch/audiostretchy.git
cd audiostretchy
git submodule update --init --recursive # To fetch the C library source
python3 -m pip install -e .
```
If you modify the C code in `vendors/stretch/`, you'll need to recompile the library. The CI workflow handles this for official releases. For local development, you'd need a C compiler (GCC/Clang on Linux/macOS, MSVC on Windows) and would manually compile `vendors/stretch/stretch.c` into the appropriate shared library (`_stretch.so`, `_stretch.dylib`, or `_stretch.dll`) and place it in the correct directory under `src/audiostretchy/interface/`.

## Usage

### CLI

The command-line interface allows you to stretch audio files directly:
```bash
audiostretchy INPUT_FILE OUTPUT_FILE [FLAGS]
```

**Positional Arguments:**
- `INPUT_FILE`: Path to the input audio file (e.g., `.wav`, `.mp3`).
- `OUTPUT_FILE`: Path to save the processed audio file.

**Flags (TDHS Parameters):**
-   `-r, --ratio=FLOAT`: The stretch ratio. >1.0 extends audio (slower), <1.0 shortens (faster). Default: `1.0`.
-   `-g, --gap_ratio=FLOAT`: Stretch ratio for silence/gaps. Default: `0.0` (uses main ratio). *Note: Effective use of `gap_ratio` depends on the C library's internal logic or future Python-side segmentation.*
-   `-u, --upper_freq=INT`: Upper frequency limit for period detection (Hz). Default: `333`.
-   `-l, --lower_freq=INT`: Lower frequency limit for period detection (Hz). Default: `55`.
-   `-b, --buffer_ms=FLOAT`: Buffer size in milliseconds for silence detection logic. Default: `25`. *(Note: Primarily for advanced gap handling not fully exposed in basic Python wrapper)*.
-   `-t, --threshold_gap_db=FLOAT`: Silence threshold in dB for gap detection. Default: `-40`. *(Note: Primarily for advanced gap handling not fully exposed in basic Python wrapper)*.
-   `-d, --double_range=BOOL`: Use extended ratio range (0.25-4.0 instead of 0.5-2.0). Default: `False`.
-   `-f, --fast_detection=BOOL`: Enable fast (but potentially lower quality) period detection. Default: `False`.
-   `-n, --normal_detection=BOOL`: Force normal period detection (overrides fast if sample rate is high). Default: `False`.
-   `-s, --sample_rate=INT`: Target sample rate in Hz for resampling (0 to disable). Default: `0`.

**Example:**
```bash
audiostretchy input.wav output_stretched.wav -r 1.2 -s 44100
```

### Python API

```python
from audiostretchy.stretch import AudioStretch, stretch_audio

# Simple function call
stretch_audio(
    input_path="input.mp3",
    output_path="output.wav",
    ratio=0.8,
    sample_rate=22050, # Resample to 22050 Hz
    upper_freq=300
)

# Using the AudioStretch class for more control
processor = AudioStretch()
processor.open("input.flac") # Pedalboard handles opening various formats

processor.stretch(
    ratio=1.1,
    gap_ratio=1.5,      # Stretch silence even more
    upper_freq=350,
    lower_freq=60,
    double_range=True   # Allow ratios like 0.25 or 4.0
)
processor.resample(target_framerate=48000) # Resample output

processor.save("processed_output.ogg", output_format="ogg") # Save as OGG
```
The `AudioStretch` class also supports opening from and saving to file-like BytesIO objects by passing the `file` argument to `open()` and `save()`, and optionally `format` if it cannot be inferred.

## Changelog

*(To be updated before release)*
- Core stretching logic remains based on David Bryant's `audio-stretch` C library (TDHS).
- Audio I/O (WAV, MP3, FLAC, OGG, etc.) and resampling are now handled by the `pedalboard` library.
- Removed direct dependencies on `pydub`, `pymp3`, `soxr`.
- Installation streamlined, `[all]` extra removed as `pedalboard` is a core dependency.
- Updated documentation and examples.

## License

- This project's Python wrapper code: Copyright (c) 2023-2024 Adam Twardoch. Licensed under the [BSD-3-Clause license](./LICENSE.txt).
- Core C library `vendors/stretch/stretch.c`: Copyright (c) David Bryant. Included under its original BSD-style license.
- Audio I/O and Resampling: Uses [Spotify's Pedalboard library](https://github.com/spotify/pedalboard) (Apache License 2.0). Pedalboard itself may use other libraries with their own licenses (e.g., libsndfile, Rubber Band library).
- Python code written with assistance from GPT-4.
