# AudioStretchy

**AudioStretchy is a Python library and command-line interface (CLI) tool designed for high-quality time-stretching of audio files without altering their pitch.**

It leverages David Bryant’s robust [audio-stretch C library](https://github.com/dbry/audio-stretch), which implements the Time-Domain Harmonic Scaling (TDHS) algorithm, particularly effective for speech. For versatile audio file handling (WAV, MP3, FLAC, OGG, etc.) and resampling, AudioStretchy integrates [Spotify's Pedalboard library](https://github.com/spotify/pedalboard).

## Table of Contents

- [Who is this for?](#who-is-this-for)
- [Why is it useful?](#why-is-it-useful)
- [Features](#features)
- [Demo](#demo)
- [Installation](#installation)
    - [Standard Installation](#standard-installation)
    - [Development Installation](#development-installation)
- [Usage](#usage)
    - [Command-Line Interface (CLI)](#command-line-interface-cli)
    - [Python API](#python-api)
- [Technical Details](#technical-details)
    - [How it Works](#how-it-works)
    - [Core Modules](#core-modules)
    - [Coding Conventions](#coding-conventions)
    - [Contributing](#contributing)
- [License](#license)

## Who is this for?

AudioStretchy is aimed at:

*   **Musicians and Music Producers:** To adjust the tempo of backing tracks, samples, or entire songs.
*   **Audio Engineers:** For post-production tasks requiring timing adjustments without pitch artifacts.
*   **Podcast and Video Editors:** To fit voiceovers or audio segments into specific time slots.
*   **Software Developers:** Who need to integrate audio time-stretching capabilities into their Python applications.
*   **Researchers and Hobbyists:** Exploring audio processing techniques.

## Why is it useful?

Time-stretching audio without affecting pitch is a common need in audio production. AudioStretchy provides:

*   **High-Quality Results:** The TDHS algorithm is known for producing natural-sounding results, especially with speech.
*   **Ease of Use:** Simple CLI and Python API make it accessible for various workflows.
*   **Format Flexibility:** Supports a wide range of common audio formats thanks to Pedalboard.
*   **Cross-Platform Compatibility:** Works on Windows, macOS, and Linux.

## Features

*   **High-Quality Time Stretching**: Utilizes David Bryant's `audio-stretch` C library (TDHS algorithm).
*   **Silence-Aware Stretching**: Supports separate stretching ratios for gaps/silence via the `gap_ratio` parameter (Note: The Python wrapper currently passes this to the C library; however, effective silence-specific stretching relies on the C library's internal segmentation or future Python-side pre-segmentation logic).
*   **Broad Audio Format Support**: Reads and writes numerous audio formats (WAV, MP3, FLAC, OGG, AIFF, etc.) using the Pedalboard library.
*   **Resampling**: Supports audio resampling, also via Pedalboard.
*   **Adjustable Parameters**: Fine-tune stretching with parameters like frequency limits for period detection, buffer sizes, and silence thresholds.
*   **Cross-Platform**: Includes pre-compiled C libraries for Windows, macOS (x86_64, arm64), and Linux.
*   **Simple CLI and Python API**.

## Demo

Below are links to a short audio file (as WAV and MP3), with the same file stretched at a ratio of 1.2 (making it 20% slower):

| Input                                                                             | Stretched (Ratio 1.2)                                                                     |
| --------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| [`audio.wav`](https://github.com/twardoch/audiostretchy/raw/main/tests/audio.wav) | [`audio-1.2.wav`](https://github.com/twardoch/audiostretchy/raw/main/tests/audio-1.2.wav) |
| [`audio.mp3`](https://github.com/twardoch/audiostretchy/raw/main/tests/audio.mp3) | [`audio-1.2.mp3`](https://github.com/twardoch/audiostretchy/raw/main/tests/audio-1.2.mp3) |

## Installation

### Standard Installation

AudioStretchy includes a C extension that provides the core TDHS algorithm. Pre-compiled wheels are provided for Windows, macOS, and Linux, making installation straightforward via pip:

```bash
python3 -m pip install audiostretchy
```

This command installs `audiostretchy` along with its key dependencies:
*   `numpy`: For numerical operations.
*   `pedalboard`: For reading/writing various audio formats and for resampling.
*   `fire`: For the command-line interface.

**Note on Pedalboard Dependencies (FFmpeg):**
For `pedalboard` to support a wide range of audio formats (especially compressed ones like MP3, M4A, OGG), it relies on system libraries like FFmpeg. If you encounter issues opening or saving specific file types, ensure FFmpeg is installed and accessible in your system's PATH.

*   **macOS (using Homebrew):** `brew install ffmpeg`
*   **Linux (Debian/Ubuntu):** `sudo apt-get install ffmpeg`
*   **Windows:** Download FFmpeg from the [official website](https://ffmpeg.org/download.html), extract it, and add its `bin` directory to your system's PATH environment variable.

### Development Installation

To install the development version from the repository for contributing or testing:

```bash
git clone https://github.com/twardoch/audiostretchy.git
cd audiostretchy
git submodule update --init --recursive # To fetch the audio-stretch C library source
python3 -m pip install -e .[testing] # Installs in editable mode with testing dependencies
```

If you modify the C code in `vendors/stretch/stretch.c`, you will need to recompile the C library. This typically involves:
1.  Having a C compiler installed (GCC/Clang on Linux/macOS, MSVC on Windows).
2.  Manually compiling `vendors/stretch/stretch.c` into the appropriate shared library format (`_stretch.so` on Linux, `_stretch.dylib` on macOS, `_stretch.dll` on Windows).
3.  Placing the compiled library into the correct directory within `src/audiostretchy/interface/` (e.g., `src/audiostretchy/interface/linux/`).
The CI workflow (`.github/workflows/ci.yaml`) handles this for official releases.

## Usage

### Command-Line Interface (CLI)

The `audiostretchy` command allows you to stretch audio files directly from your terminal.

**Syntax:**
```bash
audiostretchy INPUT_FILE OUTPUT_FILE [FLAGS]
```

**Positional Arguments:**
*   `INPUT_FILE`: Path to the input audio file (e.g., `input.wav`, `song.mp3`).
*   `OUTPUT_FILE`: Path to save the processed audio file (e.g., `output_stretched.wav`).

**Optional Flags (TDHS Parameters):**
*   `-r, --ratio=FLOAT`: The stretch ratio. Values > 1.0 extend audio (slower playback), < 1.0 shorten audio (faster playback). Default: `1.0` (no change).
*   `-g, --gap_ratio=FLOAT`: Stretch ratio specifically for silence or gaps in the audio. Default: `0.0` (which means use the main `ratio` for gaps). *Note: The underlying C library may use this if it performs internal silence detection, but the Python wrapper does not currently implement pre-segmentation based on this.*
*   `-u, --upper_freq=INT`: Upper frequency limit for period detection in Hz. Affects how the algorithm identifies fundamental frequencies. Default: `333`.
*   `-l, --lower_freq=INT`: Lower frequency limit for period detection in Hz. Default: `55`.
*   `-b, --buffer_ms=FLOAT`: Buffer size in milliseconds, potentially for silence detection logic. Default: `25`. *(Note: Primarily relevant if advanced gap handling is implemented/utilized).*
*   `-t, --threshold_gap_db=FLOAT`: Silence threshold in dB for gap detection. Default: `-40`. *(Note: Primarily relevant if advanced gap handling is implemented/utilized).*
*   `-d, --double_range=BOOL`: Use an extended ratio range (0.25-4.0 instead of the default 0.5-2.0). Set to `True` or `False`. Default: `False`.
*   `-f, --fast_detection=BOOL`: Enable a faster (but potentially lower quality) period detection method. Set to `True` or `False`. Default: `False`.
*   `-n, --normal_detection=BOOL`: Force normal period detection (this can override fast detection if the sample rate is high, depending on C library logic). Set to `True` or `False`. Default: `False`.
*   `-s, --sample_rate=INT`: Target sample rate in Hz for resampling the output. If `0` or omitted, the output will have the same sample rate as the input (unless stretching itself inherently changes it, which TDHS does not aim to do for sample rate). Default: `0` (no resampling).

**Example:**
To make `input.mp3` 20% slower and save it as `output_slow.wav` with a 44100 Hz sample rate:
```bash
audiostretchy input.mp3 output_slow.wav --ratio 1.2 --sample_rate 44100
```

### Python API

AudioStretchy can be used programmatically within your Python scripts.

**Simple Function Call:**
The `stretch_audio` function provides a quick way to process files.

```python
from audiostretchy.stretch import stretch_audio

stretch_audio(
    input_path="path/to/your/input.mp3",
    output_path="path/to/your/output_stretched.wav",
    ratio=0.8,  # Make audio 20% faster
    sample_rate=22050, # Resample output to 22050 Hz
    upper_freq=300, # Adjust upper frequency for period detection
    fast_detection=True # Use faster algorithm
)

print("Audio stretching complete!")
```

**Using the `AudioStretch` Class:**
For more control, or if working with audio data in memory (e.g., from `BytesIO` objects), use the `AudioStretch` class.

```python
from audiostretchy.stretch import AudioStretch
from io import BytesIO

# Initialize the processor
processor = AudioStretch()

# --- Example 1: Processing files ---
processor.open("input.flac") # Pedalboard handles opening various formats

processor.stretch(
    ratio=1.1,          # Make 10% slower
    # gap_ratio=1.5,    # Stretch silence even more (see note on gap_ratio effectiveness)
    upper_freq=350,
    lower_freq=60,
    double_range=True   # Allow ratios like 0.25 or 4.0
)

# Optional: Resample the processed audio
processor.resample(target_framerate=48000)

processor.save("processed_output.ogg") # Pedalboard infers format from extension
# OR: processor.save("processed_output.custom", output_format="ogg")


# --- Example 2: Processing from BytesIO ---
# Assuming `input_audio_bytes` is a bytes object containing audio data (e.g., read from a stream)
# and `input_format` is known (e.g., 'wav', 'mp3')

# input_audio_bytes = b"..." # Your audio data
# input_format = "wav"
#
# input_file_like_object = BytesIO(input_audio_bytes)
# processor.open(file=input_file_like_object, format=input_format) # `format` might be needed if not inferable
#
# processor.stretch(ratio=1.5)
#
# output_file_like_object = BytesIO()
# processor.save(file=output_file_like_object, format="mp3") # Specify output format
#
# stretched_audio_bytes = output_file_like_object.getvalue()
# with open("output_from_bytesio.mp3", "wb") as f:
#     f.write(stretched_audio_bytes)

```

## Technical Details

### How it Works

AudioStretchy operates through several key stages:

1.  **Audio Input/Output & Resampling (via `Pedalboard`):**
    *   When an input file is provided (e.g., MP3, WAV, FLAC), `pedalboard` is used to decode it into raw audio samples (specifically, a NumPy array of `float32` values). It also reads metadata like sample rate and channel count.
    *   If resampling is requested, `pedalboard` handles this efficiently.
    *   After processing, `pedalboard` encodes the modified audio samples back into the desired output format.

2.  **Core Time-Stretching (via `audio-stretch` C library & `TDHSAudioStretch` wrapper):**
    *   The raw audio samples (float32) obtained from `pedalboard` are converted to 16-bit integers (`int16`), as the C library expects this format. If the audio is stereo, channels are interleaved (L, R, L, R...).
    *   The `TDHSAudioStretch` class in `src/audiostretchy/interface/tdhs.py` uses `ctypes` to call functions from the pre-compiled `audio-stretch` shared library (e.g., `_stretch.so`, `_stretch.dylib`, `_stretch.dll`).
    *   The C library implements **Time-Domain Harmonic Scaling (TDHS)**. This algorithm works by:
        *   Analyzing the input audio signal in the time domain.
        *   Identifying periodic segments (related to pitch) within the audio.
        *   To slow down audio (stretch ratio > 1.0), it intelligently repeats these small segments.
        *   To speed up audio (stretch ratio < 1.0), it removes some of these segments.
        *   This is done in a way that aims to preserve the harmonic structure and formants, thus maintaining the original pitch and timbre.
    *   Parameters like `upper_freq` and `lower_freq` guide the C library in its period detection, defining the expected range of fundamental frequencies in the audio.
    *   Flags like `STRETCH_FAST_FLAG` (for `--fast_detection`) and `STRETCH_DUAL_FLAG` (for `--double_range`) modify the C library's behavior.
    *   After the C library processes the audio, the resulting `int16` samples are converted back to `float32` for `pedalboard` to handle.

3.  **Python Orchestration (`AudioStretch` class):**
    *   The `AudioStretch` class in `src/audiostretchy/stretch.py` manages the overall process:
        *   Initializes and uses `PedalboardAudioFile` for I/O.
        *   Prepares data for the `TDHSAudioStretch` wrapper (data type conversion, interleaving).
        *   Calls the `stretch` method of `TDHSAudioStretch`.
        *   Handles data conversion back from the wrapper.
        *   Coordinates resampling if requested.

The `gap_ratio` parameter is intended for applying a different stretch ratio to silent portions of the audio. While the Python wrapper passes this to the C library initialization, the current Python implementation of `AudioStretch.stretch()` processes the entire audio with the primary `ratio`. Effective utilization of `gap_ratio` would typically require the Python code to segment the audio into speech/silence parts first (e.g., based on RMS levels and `threshold_gap_db`), and then apply different ratios to these segments, or for the C library to have internal advanced segmentation logic that uses this parameter. The original C CLI application (`main.c` in `dbry/audio-stretch`) contains such segmentation logic, which is not fully replicated in the current Python bindings.

### Core Modules

*   **`src/audiostretchy/__main__.py`:**
    *   Provides the command-line interface using the `fire` library.
    *   It calls the `stretch_audio` function from `stretch.py`.
*   **`src/audiostretchy/stretch.py`:**
    *   Contains the main `AudioStretch` class that orchestrates the audio processing.
    *   Implements methods for opening, stretching, resampling, and saving audio.
    *   Includes the `stretch_audio` convenience function used by the CLI.
    *   Relies on `pedalboard` for I/O and resampling, and `TDHSAudioStretch` for the core algorithm.
*   **`src/audiostretchy/interface/tdhs.py`:**
    *   Defines the `TDHSAudioStretch` class, which is a Python `ctypes` wrapper around the pre-compiled `audio-stretch` C library.
    *   Loads the shared library (`.so`, `.dylib`, `.dll`) based on the operating system.
    *   Defines argument types and return types for the C functions (`stretch_init`, `stretch_samples`, `stretch_flush`, etc.).
*   **`src/audiostretchy/interface/{win,mac,linux}/`:**
    *   These directories contain the pre-compiled shared C libraries (`_stretch.dll`, `_stretch.dylib`, `_stretch.so`) for different platforms and architectures.
*   **`vendors/stretch/`:**
    *   Contains the source code of David Bryant's `audio-stretch` C library as a Git submodule. This is used for compiling the shared libraries.

### Coding Conventions

This project adheres to standard Python coding practices and uses tools to maintain code quality:

*   **Formatting:** Code is formatted using [Black](https://github.com/psf/black).
*   **Import Sorting:** Imports are sorted using [isort](https://pycqa.github.io/isort/). Configuration is in `.isort.cfg`.
*   **Linting:** Code is linted using [Flake8](https://flake8.pycqa.org/en/latest/). Configuration is in `pyproject.toml` (`[tool.flake8]`).
*   **Pre-commit Hooks:** The `.pre-commit-config.yaml` file defines hooks that run these tools automatically before commits, ensuring consistency. This includes checks for trailing whitespace, large files, valid syntax, etc.

### Contributing

Contributions are welcome! If you'd like to contribute, please follow these general guidelines:

1.  **Fork the Repository:** Create your own fork of the `audiostretchy` repository on GitHub.
2.  **Clone Your Fork:**
    ```bash
    git clone https://github.com/YOUR_USERNAME/audiostretchy.git
    cd audiostretchy
    git submodule update --init --recursive
    ```
3.  **Create a Branch:** Create a new branch for your feature or bug fix:
    ```bash
    git checkout -b my-new-feature
    ```
4.  **Set Up Development Environment:**
    *   It's recommended to use a virtual environment:
        ```bash
        python3 -m venv venv
        source venv/bin/activate  # On Windows: venv\Scripts\activate
        ```
    *   Install the project in editable mode with testing dependencies:
        ```bash
        python3 -m pip install -e .[testing]
        ```
    *   Install pre-commit hooks:
        ```bash
        pre-commit install
        ```
5.  **Make Your Changes:** Implement your feature or bug fix.
    *   Adhere to the coding conventions (Black, isort, Flake8). The pre-commit hooks will help with this.
    *   Write tests for any new functionality in the `tests/` directory.
6.  **Run Tests:** Ensure all tests pass:
    ```bash
    pytest
    ```
    Check test coverage:
    ```bash
    pytest --cov src/audiostretchy --cov-report term-missing
    ```
7.  **Commit Your Changes:**
    ```bash
    git add .
    git commit -m "feat: Add new feature X" # Or "fix: Resolve bug Y"
    ```
8.  **Push to Your Fork:**
    ```bash
    git push origin my-new-feature
    ```
9.  **Submit a Pull Request:** Open a pull request from your branch to the `main` branch of the original `twardoch/audiostretchy` repository. Provide a clear description of your changes.

If you plan to modify the C library code in `vendors/stretch/`, you will also need to recompile it for your platform and potentially update the CI workflows if changes are significant.

## License

*   The Python wrapper code for AudioStretchy (this project) is licensed under the **BSD-3-Clause License**. See [LICENSE.txt](./LICENSE.txt). Copyright (c) 2023-2024 Adam Twardoch.
*   The core C library `vendors/stretch/stretch.c` is Copyright (c) David Bryant and is included under its original BSD-style license.
*   Audio I/O and Resampling functionalities are provided by [Spotify's Pedalboard library](https://github.com/spotify/pedalboard), which is licensed under the Apache License 2.0. Pedalboard itself may utilize other libraries with their own respective licenses (e.g., libsndfile, Rubber Band library).
*   Some Python code may have been written with assistance from AI language models.

_Current Version: (to be updated by release process)_
