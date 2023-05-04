# AudioStretchy

AudioStretchy is a Python library that allows you to time-stretch audio signals without changing their pitch. It is a wrapper around David Bryant’s [audio-stretch](https://github.com/dbry/audio-stretch) library by David Bryant, which implements a sophisticated time-stretching algorithm for high-quality results. 

Version: 1.2.0

## Features

- Time stretching of audio files without changing their pitch
- Supports WAV files, and optionally MP3 files
- Adjustable stretching ratio from 0.25 to 4.0
- Cross-platform: Windows, macOS, and Linux
- Optional resampling

The following explanation is adapted from the [original audio-stretch C library](https://github.com/dbry/audio-stretch): 

Time-domain harmonic scaling (TDHS) is a method for time-scale
modification of speech (or other audio signals), allowing the apparent
rate of speech articulation to be changed without affecting the
pitch-contour and the time-evolution of the formant structure. TDHS
differs from other time-scale modification algorithms in that
time-scaling operations are performed in the time domain (not the
frequency domain).

This project is a Python wrapper around a a TDHS library to utilize it with standard WAV files. 

There are two effects possible with TDHS and the audio-stretch demo. The
first is the more obvious mentioned above of changing the duration (or
speed) of a speech (or other audio) sample without modifying its pitch.
The other effect is similar, but after applying the duration change we
change the sampling rate in a complimentary manner to restore the original
duration and timing, which then results in the pitch being altered.

So when a ratio is supplied to the audio-stretch program, the default
operation is for the total duration of the audio file to be scaled by
exactly that ratio (0.5X to 2.0X), with the pitches remaining constant.
If the option to scale the sample-rate proportionally is specified (-s)
then the total duration and timing of the audio file will be preserved,
but the pitches will be scaled by the specified ratio instead. This is
useful for creating a "helium voice" effect and lots of other fun stuff.

Note that unless ratios of exactly 0.5 or 2.0 are used with the -s option,
non-standard sampling rates will probably result. Many programs will still
properly play these files, and audio editing programs will likely import
them correctly (by resampling), but it is possible that some applications
will barf on them. They can also be resampled to a standard rate using
[audio-resampler](https://github.com/dbry/audio-resampler) by David Bryant. 

_Note: The Python package does not expose all command-line options of the original library._

## Installation

### Simple installation

To be able to stretch and resample WAV and MP3 files, install AudioStretchy using `pip` like so:

```
pip install audiostretchy[all]
```

### Efficient installation

To only be able to stretch WAV files, install AudioStretchy without dependencies like so: 


```
pip install audiostretchy
```

### Development installation

To install the development version, use:

```
python3 -m pip install git+https://github.com/twardoch/audiostretchy#egg=audiostretchy[all]
```

## Usage

### CLI

```
audiostretchy INPUT_WAV OUTPUT_WAV <flags>

POSITIONAL ARGUMENTS
    INPUT_WAV
    OUTPUT_WAV

FLAGS
    -r, --ratio=RATIO
        Default: 1.0
    -g, --gap_ratio=GAP_RATIO
        Default: 0.0
    -u, --upper_freq=UPPER_FREQ
        Default: 333
    -l, --lower_freq=LOWER_FREQ
        Default: 55
    -b, --buffer_ms=BUFFER_MS
        Default: 25
    -t, --threshold_gap_db=THRESHOLD_GAP_DB
        Default: -40
    -d, --dual_force=DUAL_FORCE
        Default: False
    -f, --fast_detection=FAST_DETECTION
        Default: False
    -n, --normal_detection=NORMAL_DETECTION
        Default: False
    -s, --sample_rate=SAMPLE_RATE
        Default: 0
```

### Python

```python
from audiostretchy.stretch import stretch_audio

stretch_audio("input.wav", "output.wav", ratio=ratio)
```

In this example, the `input.wav` file will be time-stretched by a factor of 1.1, meaning it will be 10% longer, and the result will be saved in the `output.wav` file.

For advanced usage, you can use the `AudioStretch` class (docs to be provided).


## License

- [Original C library code](https://github.com/dbry/audio-stretch): Copyright (c) 2022 David Bryant
- [Python code](https://github.com/twardoch/audiostretchy): Copyright (c) 2023 Adam Twardoch
- Written with assistance from GPT-4
- Licensed under the [BSD-3-Clause license](./LICENSE.txt)
