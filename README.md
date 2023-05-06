# AudioStretchy

AudioStretchy is a Python library and CLI tool that which performs fast, high-quality time-stretching of WAV/MP3 files without changing their pitch. Works well for speech, can time-stretch silence separately. The library is a wrapper around David Bryant’s [audio-stretch](https://github.com/dbry/audio-stretch) C library. 

Version: 1.2.3

## Features

- Fast, high-quality time stretching of audio files without changing their pitch
- Adjustable stretching ratio from 0.25 to 4.0
- Cross-platform: Windows, macOS, and Linux
- Supports WAV files and file-like objects. With `[all]` installation, also supports MP3 files and file-like objects
- With `[all]` installation, also supports resampling

**Time-domain harmonic scaling (TDHS)** is a method for time-scale modification of speech (or other audio signals), allowing the apparent rate of speech articulation to be changed without affecting the pitch-contour and the time-evolution of the formant structure. TDHS differs from other time-scale modification algorithms in that time-scaling operations are performed in the time domain (not the frequency domain).

The core functionality of this package is provided by David Bryant’s excellent [audio-stretch C library](https://github.com/dbry/audio-stretch) that performs fast, high-quality TDHS on WAV in the ratio range of 0.25 (4× slower) to 4.0 (4× faster). 

The library gives very good results with speech recordings, especially with modest stretching at the ratio between 0.9 (10% slower) and 1.1 (10% faster). AudioStretchy is a Python wrapper around that library. The Python package also offers some additional, optional functionality: supports MP3 (in addition to WAV), and allows you to preform resampling.

## Installation

### Full installation

To be able to **stretch** and **resample** both **WAV** and **MP3** files, install AudioStretchy using `pip` like so:

```
pip install audiostretchy[all]
```

This installs the package and the pre-compiled `audio-stretch` libraries for macOS, Windows and Linux. 

This also installs optional dependencies: 

- for MP3 support: [pydub](https://pypi.org/project/pydub/) on macOS, [pymp3](https://pypi.org/project/pymp3/) on Linux and Windows
- for resampling: [soxr](https://pypi.org/project/soxr/)

On macOS, you also need to install [HomeBrew](https://brew.sh/) and then in Terminal run: 

```bash
brew install ffmpeg
```

### Minimal installation

To only be able to **stretch** **WAV** files (no resampling, no MP3 support), install AudioStretchy with minimal dependencies like so: 

```
pip install audiostretchy
```

This only installs the package and the pre-compiled `audio-stretch` libraries for macOS, Windows and Linux. 

### Full development installation

To install the development version, use:

```
python3 -m pip install git+https://github.com/twardoch/audiostretchy#egg=audiostretchy[all]
```

## Usage

### CLI

```
audiostretchy INPUT_WAV OUTPUT_WAV <flags>

POSITIONAL ARGUMENTS
    INPUT_PATH
        The path to the input WAV or MP3 audio file.
    OUTPUT_PATH
        The path to save the stretched WAV or MP3 audio file.

FLAGS
    -r, --ratio=RATIO
        The stretch ratio, where values greater than 1.0 will extend the audio and values less than 1.0 will shorten the audio. From 0.5 to 2.0, or with `-d` from 0.25 to 4.0. Default is 1.0 = no stretching.
    -g, --gap_ratio=GAP_RATIO
        The stretch ratio for gaps (silence) in the audio. Default is 0.0 = uses ratio.
    -u, --upper_freq=UPPER_FREQ
        The upper frequency limit for period detection in Hz. Default is 333 Hz.
    -l, --lower_freq=LOWER_FREQ
        The lower frequency limit. Default is 55 Hz.
    -b, --buffer_ms=BUFFER_MS
        The buffer size in milliseconds for processing the audio in chunks (useful with `-g`). Default is 25 ms.
    -t, --threshold_gap_db=THRESHOLD_GAP_DB
        The threshold level in dB to determine if a section of audio is considered a gap (for `-g`). Default is -40 dB.
    -d, --double_range=DOUBLE_RANGE
        If set, doubles the min/max range of stretching.
    -f, --fast_detection=FAST_DETECTION
        If set, enables fast period detection, which may speed up processing but reduce the quality of the stretched audio.
    -n, --normal_detection=NORMAL_DETECTION
        If set, forces the algorithm to use normal period detection instead of fast period detection.
    -s, --sample_rate=SAMPLE_RATE
        The target sample rate for resampling the stretched audio in Hz (if installed with `[all]`). Default is 0 = use sample rate of the input audio.
```

### Python

```python
from audiostretchy.stretch import stretch_audio

stretch_audio("input.wav", "output.wav", ratio=1.1)
```

In this example, the `input.wav` file will be time-stretched by a factor of 1.1, meaning it will be 10% longer, and the result will be saved in the `output.wav` file.

For advanced usage, you can use the `AudioStretch` class that lets you open and save files provided as paths or as file-like BytesIO objects: 

```python
from audiostretchy.stretch import AudioStretch

audio_stretch = AudioStretch()
audio_stretch.open(file=MP3DataAsBytesIO, format="mp3") # Needs [all] installation for MP3 support
audio_stretch.stretch(
    ratio=1.1,
    gap_ratio=1.2,
    upper_freq=333,
    lower_freq=55,
    buffer_ms=25,
    threshold_gap_db=-40,
    dual_force=False,
    fast_detection=False,
    normal_detection=False,
)
audio_stretch.resample(sample_rate=44100) # Needs [all] installation for soxr support
audio_stretch.save(file=WAVDataAsBytesIO, format="wav")
```


## License

- [Original C library code](https://github.com/dbry/audio-stretch): Copyright (c) 2022 David Bryant
- [Python code](https://github.com/twardoch/audiostretchy): Copyright (c) 2023 Adam Twardoch
- Written with assistance from GPT-4
- Licensed under the [BSD-3-Clause license](./LICENSE.txt)
