# AudioStretchy

AudioStretchy is a Python library that allows you to time-stretch audio signals without changing their pitch. It is a wrapper around the [audio-stretch](https://github.com/dbry/audio-stretch) library by David Bryant, which implements a sophisticated time-stretching algorithm for high-quality results. 

Version: 1.1.2

## Features

- Time stretching of audio files without changing their pitch
- Supports WAV files
- Adjustable stretching ratio from 0.25 to 4.0
- Cross-platform: Windows, macOS, and Linux

Adapted from the [original audio-stretch C library](https://github.com/dbry/audio-stretch): 

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

The Python package does not expose all command-line options of the original library. 

## Installation

Install AudioStretchy using pip:

```
python3 -m pip install audiostretchy
```

or

```
python3 -m pip install git+https://github.com/twardoch/audiostretchy
```

## Usage

### CLI

```
audiostretchy INFILENAME OUTFILENAME <flags>

POSITIONAL ARGUMENTS
    INFILENAME
        The path to the input WAV file.
    OUTFILENAME
        The path to the output WAV file.

FLAGS
    -r, --ratio=RATIO
        Type: float
        Default: 1.0
        The ratio to use for processing. Defaults to 1.0.
    -s, --silence_ratio=SILENCE_RATIO
        Type: float
        Default: 0.0
        The silence ratio to use for processing if different from ratio
```

### Python

```python
from audiostretchy.stretch import process_audio

input_file = "input.wav"
output_file = "output.wav"
stretch_ratio = 1.1

process_audio(input_file, output_file, ratio=stretch_ratio)
```

In this example, the `input.wav` file will be time-stretched by a factor of 1.1, meaning it will be 10% longer, and the result will be saved in the `output.wav` file.

## API

The main function to use in AudioStretchy is `process_audio` in `audiostretchy.stretch`:

```python
process_audio(
    infilename: Union[str, Path],
    outfilename: Union[str, Path],
    ratio: float = 1.0,
    silence_ratio: float = 0.0,
)
```

- `infilename`: The path to the input audio file (WAV format).
- `outfilename`: The path to the output audio file (WAV format).
- `ratio`: The stretching ratio. Must be between 0.25 and 4.0. Defaults to 1.0 (no stretching).
- `silence_ratio`: The silence ratio to use for processing. Must be between 0.25 and 4.0. Defaults to 0.0 (use the same ratio as `ratio`).

## License

- [Original C library code](https://github.com/dbry/audio-stretch): Copyright (c) 2022 David Bryant
- [Python code](https://github.com/twardoch/audiostretchy): Copyright (c) 2023 Adam Twardoch
- Licensed under the [BSD-3-Clause license](./LICENSE.txt)
