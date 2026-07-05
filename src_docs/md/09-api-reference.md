---
# this_file: src_docs/md/09-api-reference.md
title: API Reference
description: Complete API documentation with examples
---

# API Reference

Complete reference for all AudioStretchy classes, functions, and modules.

## Main Functions

### `stretch_audio()`

The primary convenience function for audio time-stretching.

```python
def stretch_audio(
    input_path: str,
    output_path: str,
    ratio: float = 1.0,
    gap_ratio: float = 0.0,
    upper_freq: int = 333,
    lower_freq: int = 55,
    buffer_ms: float = 25.0,
    threshold_gap_db: float = -40.0,
    double_range: bool = False,
    fast_detection: bool = False,
    normal_detection: bool = False,
    sample_rate: int = 0
) -> None
```

**Parameters:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `input_path` | str | - | Path to input audio file |
| `output_path` | str | - | Path for output audio file |
| `ratio` | float | 1.0 | Stretch ratio (>1.0 = slower, <1.0 = faster) |
| `gap_ratio` | float | 0.0 | Separate ratio for silence/gaps |
| `upper_freq` | int | 333 | Upper frequency limit for period detection (Hz) |
| `lower_freq` | int | 55 | Lower frequency limit for period detection (Hz) |
| `buffer_ms` | float | 25.0 | Buffer size in milliseconds |
| `threshold_gap_db` | float | -40.0 | Silence detection threshold (dB) |
| `double_range` | bool | False | Enable extended ratio range (0.25-4.0) |
| `fast_detection` | bool | False | Use faster detection algorithm |
| `normal_detection` | bool | False | Force normal detection algorithm |
| `sample_rate` | int | 0 | Target output sample rate (0 = preserve) |

**Raises:**

- `FileNotFoundError`: Input file doesn't exist
- `ValueError`: Invalid parameters  
- `RuntimeError`: Processing errors

**Example:**

```python
from audiostretchy import stretch_audio

# Basic usage
stretch_audio("input.mp3", "output.wav", ratio=1.2)

# Advanced usage
stretch_audio(
    "speech.wav",
    "slow_speech.wav", 
    ratio=1.5,
    upper_freq=300,
    lower_freq=80,
    normal_detection=True
)
```

## Core Classes

### `AudioStretch`

Main class for audio processing with fine-grained control.

```python
class AudioStretch:
    """
    Audio time-stretching processor using TDHS algorithm.
    
    Provides high-level interface for loading, processing, and saving
    audio files with time-stretching capabilities.
    """
```

#### Constructor

```python
def __init__(self) -> None
```

Creates a new AudioStretch instance.

**Example:**

```python
from audiostretchy import AudioStretch

processor = AudioStretch()
```

#### Methods

##### `open()`

```python
def open(
    self, 
    file: Union[str, Path, BinaryIO],
    format: Optional[str] = None
) -> None
```

Load an audio file for processing.

**Parameters:**

- `file`: File path (str/Path) or file-like object (BinaryIO)
- `format`: Audio format hint (e.g., "wav", "mp3") for file-like objects

**Raises:**

- `FileNotFoundError`: File doesn't exist
- `RuntimeError`: Cannot load audio file

**Examples:**

```python
# From file path
processor.open("audio.mp3")

# From file-like object
from io import BytesIO
with open("audio.wav", "rb") as f:
    data = BytesIO(f.read())
processor.open(data, format="wav")
```

##### `stretch()`

```python
def stretch(
    self,
    ratio: float = 1.0,
    gap_ratio: float = 0.0,
    upper_freq: int = 333,
    lower_freq: int = 55,
    buffer_ms: float = 25.0,
    threshold_gap_db: float = -40.0,
    double_range: bool = False,
    fast_detection: bool = False,
    normal_detection: bool = False
) -> None
```

Apply time-stretching to the loaded audio.

**Parameters:** Same as `stretch_audio()` function (except file paths)

**Raises:**

- `ValueError`: Invalid parameters or no audio loaded
- `RuntimeError`: Processing errors

**Example:**

```python
processor.open("input.wav")
processor.stretch(ratio=1.3, upper_freq=350)
```

##### `resample()`

```python
def resample(self, target_samplerate: int) -> None
```

Resample the audio to a different sample rate.

**Parameters:**

- `target_samplerate`: Target sample rate in Hz

**Raises:**

- `ValueError`: Invalid sample rate or no audio loaded
- `RuntimeError`: Resampling errors

**Example:**

```python
processor.resample(48000)
```

##### `save()`

```python
def save(
    self,
    file: Union[str, Path, BinaryIO],
    format: Optional[str] = None
) -> None
```

Save the processed audio to file.

**Parameters:**

- `file`: Output file path or file-like object
- `format`: Output format (inferred from extension if not specified)

**Raises:**

- `RuntimeError`: Save errors or no audio processed

**Examples:**

```python
# Save to file
processor.save("output.wav")

# Save to file-like object
from io import BytesIO
output_buffer = BytesIO()
processor.save(output_buffer, format="mp3")
```

#### Properties

##### `audio_file`

```python
@property
def audio_file(self) -> Optional[PedalboardAudioFile]
```

Access to the underlying Pedalboard audio file object.

##### `sample_rate`

```python
@property
def sample_rate(self) -> Optional[float]
```

Sample rate of the loaded audio file.

##### `channels`

```python
@property
def channels(self) -> Optional[int]
```

Number of audio channels.

#### Complete Example

```python
from audiostretchy import AudioStretch

# Initialize processor
processor = AudioStretch()

try:
    # Load audio
    processor.open("input.flac")
    print(f"Loaded: {processor.sample_rate} Hz, {processor.channels} channels")
    
    # Process with custom parameters
    processor.stretch(
        ratio=1.2,
        upper_freq=400,
        lower_freq=60,
        normal_detection=True
    )
    
    # Optional resampling
    processor.resample(44100)
    
    # Save result
    processor.save("output.wav")
    print("Processing complete!")
    
except Exception as e:
    print(f"Error: {e}")
```

## Interface Classes

### `TDHSAudioStretch`

Low-level interface to the TDHS C library.

```python
class TDHSAudioStretch:
    """
    Direct interface to TDHS C library.
    
    Low-level wrapper around the audio-stretch C library using ctypes.
    Most users should use AudioStretch class instead.
    """
```

#### Constructor

```python
def __init__(self) -> None
```

Initialize the TDHS wrapper and load platform-specific library.

**Raises:**

- `RuntimeError`: Platform not supported or library not found

#### Methods

##### `init()`

```python
def init(
    self,
    sample_rate: int,
    channels: int,
    ratio: float,
    **kwargs
) -> ctypes.c_void_p
```

Initialize TDHS processing context.

**Parameters:**

- `sample_rate`: Audio sample rate
- `channels`: Number of audio channels (1 or 2)
- `ratio`: Stretch ratio
- `**kwargs`: Additional TDHS parameters

**Returns:** Opaque context pointer

##### `process()`

```python
def process(
    self,
    context: ctypes.c_void_p,
    audio_data: np.ndarray
) -> np.ndarray
```

Process audio samples through TDHS algorithm.

**Parameters:**

- `context`: Context from `init()`
- `audio_data`: Int16 audio samples

**Returns:** Processed Int16 audio samples

##### `cleanup()`

```python
def cleanup(self, context: ctypes.c_void_p) -> None
```

Clean up processing context and free memory.

**Example:**

```python
from audiostretchy.c_interface import TDHSAudioStretch
import numpy as np

# Low-level usage (advanced)
tdhs = TDHSAudioStretch()
context = tdhs.init(44100, 2, 1.2)

# Process audio chunk
audio_chunk = np.random.randint(-32768, 32767, 1000, dtype=np.int16)
processed = tdhs.process(context, audio_chunk)

# Clean up
tdhs.cleanup(context)
```

## Utility Functions

### File Format Support

AudioStretchy supports various audio formats through Pedalboard:

#### Supported Input Formats

- **Lossless**: WAV, FLAC, AIFF, BWF, RF64
- **Lossy**: MP3, OGG, M4A, AAC
- **Raw**: Raw audio with format specification

#### Supported Output Formats

Output format is determined by file extension:

```python
# Format examples
processor.save("output.wav")    # WAV
processor.save("output.mp3")    # MP3
processor.save("output.flac")   # FLAC
processor.save("output.ogg")    # OGG Vorbis
processor.save("output.m4a")    # AAC in M4A container
```

### Error Classes

#### `ParameterError`

```python
class ParameterError(ValueError):
    """Raised when invalid parameters are provided."""
    pass
```

#### `ProcessingError`

```python
class ProcessingError(RuntimeError):
    """Raised when audio processing fails."""
    pass
```

## Module Structure

### `audiostretchy.core`

Main module containing user-facing classes and functions.

**Exports:**
- `AudioStretch` class
- `stretch_audio()` function

### `audiostretchy.c_interface`

Low-level TDHS C library interface.

**Exports:**
- `TDHSAudioStretch` class

### `audiostretchy.core`

Core utilities and re-exports.

**Exports:**
- Re-exports from other modules

## Command Line Interface

### CLI Function

The CLI is implemented using Python Fire:

```python
def main() -> None:
    """CLI entry point using Fire."""
    fire.Fire(stretch_audio)
```

### Usage

```bash
# Basic usage
audiostretchy input.wav output.wav --ratio 1.2

# All parameters
audiostretchy input.mp3 output.wav \
    --ratio 1.5 \
    --upper_freq 300 \
    --lower_freq 80 \
    --fast_detection True \
    --sample_rate 44100
```

### Help

```bash
# Get help
audiostretchy --help

# Parameter help
audiostretchy input.wav output.wav --help
```

## Type Hints

AudioStretchy provides comprehensive type hints:

```python
from typing import Union, Optional, BinaryIO
from pathlib import Path
import numpy as np

# Type aliases used throughout the codebase
AudioData = np.ndarray
FilePath = Union[str, Path]
FileOrPath = Union[FilePath, BinaryIO]
```

## Examples Collection

### Basic Processing

```python
# Simple time-stretching
stretch_audio("input.wav", "output.wav", ratio=1.2)
```

### Advanced Processing

```python
# High-quality speech processing
stretch_audio(
    "speech.wav",
    "processed.wav",
    ratio=1.4,
    upper_freq=300,
    lower_freq=80,
    normal_detection=True,
    gap_ratio=1.0
)
```

### Batch Processing

```python
from pathlib import Path

input_dir = Path("input_files")
output_dir = Path("output_files")
output_dir.mkdir(exist_ok=True)

for audio_file in input_dir.glob("*.wav"):
    output_file = output_dir / f"stretched_{audio_file.name}"
    stretch_audio(str(audio_file), str(output_file), ratio=1.3)
```

### Memory-Efficient Processing

```python
from io import BytesIO

# Process without intermediate files
with open("input.mp3", "rb") as f:
    input_data = BytesIO(f.read())

output_data = BytesIO()

processor = AudioStretch()
processor.open(input_data, format="mp3")
processor.stretch(ratio=1.2)
processor.save(output_data, format="wav")

# Get processed data
result = output_data.getvalue()
```

### Error Handling

```python
def safe_stretch(input_path, output_path, **params):
    """Stretch audio with comprehensive error handling."""
    try:
        stretch_audio(input_path, output_path, **params)
        return True
    except FileNotFoundError:
        print(f"Input file not found: {input_path}")
    except ValueError as e:
        print(f"Invalid parameters: {e}")
    except RuntimeError as e:
        print(f"Processing failed: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    return False
```

## Performance Notes

### Memory Usage

- **File Loading**: ~1x file size in memory
- **Processing**: ~2x audio size peak usage
- **Streaming**: Constant memory with chunked processing

### Processing Speed

Typical processing speeds (varies by hardware):

| Content Type | Speed Factor | Notes |
|--------------|--------------|-------|
| Speech | 5-10x real-time | Fast processing |
| Music | 3-8x real-time | Depends on complexity |
| Complex Audio | 2-5x real-time | Dense harmonic content |

### Optimization Tips

1. **Use `fast_detection=True`** for development/testing
2. **Lower `sample_rate`** for faster processing
3. **Smaller `buffer_ms`** reduces latency
4. **Chunked processing** for large files

## Frequently Asked Questions

### Q: What audio formats are supported?

A: AudioStretchy supports most common formats through Pedalboard: WAV, MP3, FLAC, OGG, M4A, AIFF. For compressed formats, FFmpeg must be installed.

### Q: Can I process very long audio files?

A: Yes, AudioStretchy handles large files efficiently. For extremely large files (>1GB), consider processing in chunks using the `AudioStretch` class.

### Q: How accurate is the stretching?

A: Duration accuracy is typically within 0.1% of the target ratio. Quality depends on content type and parameters.

### Q: Can I use this for real-time processing?

A: The current implementation is designed for file processing. Real-time capabilities are planned for future releases.

### Q: What's the difference between `fast_detection` and `normal_detection`?

A: `fast_detection=True` uses a faster algorithm with slightly lower quality. `normal_detection=True` forces high-quality processing. Default is automatic selection.

### Q: How do I choose the right frequency parameters?

A: Match the parameters to your content: speech (80-300 Hz), music (50-400 Hz), bass-heavy (30-450 Hz). See [Parameters Reference](07-parameters-reference.md) for details.

### Q: Can I stretch multiple files in parallel?

A: Yes, AudioStretchy is thread-safe. You can use `concurrent.futures` or similar for parallel processing.

### Q: What platforms are supported?

A: Windows (x64), macOS (x64, ARM64), and Linux (x64) are officially supported with pre-compiled binaries.

Next: Return to [Home](index.md) or explore [How It Works](05-how-it-works.md)