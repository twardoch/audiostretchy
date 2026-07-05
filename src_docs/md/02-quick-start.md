---
# this_file: src_docs/md/02-quick-start.md
title: Quick Start
description: Basic usage examples to get you up and running
---

# Quick Start

Get up and running with AudioStretchy in minutes. This guide covers the most common use cases with practical examples.

## Basic Concepts

Before diving in, understand these key concepts:

- **Stretch Ratio**: Controls time-stretching (>1.0 = slower, <1.0 = faster)
- **Pitch Preservation**: Duration changes without affecting pitch
- **TDHS Algorithm**: Time-Domain Harmonic Scaling for natural sound

## Command Line Usage

### Simple Time Stretching

Make audio 20% slower (ratio = 1.2):

```bash
audiostretchy input.mp3 output.wav --ratio 1.2
```

Make audio 25% faster (ratio = 0.75):

```bash
audiostretchy speech.wav faster.wav --ratio 0.75
```

### Common Parameters

Add sample rate conversion:

```bash
audiostretchy music.flac output.wav --ratio 1.1 --sample_rate 44100
```

Optimize for speech with frequency limits:

```bash
audiostretchy podcast.mp3 stretched.wav --ratio 1.3 --upper_freq 300 --lower_freq 80
```

Enable fast mode for quicker processing:

```bash
audiostretchy large_file.wav output.wav --ratio 0.9 --fast_detection true
```

## Python API Usage

### Quick Function Call

The simplest approach using the `stretch_audio` function:

```python
from audiostretchy import stretch_audio

# Basic stretching
stretch_audio("input.mp3", "output.wav", ratio=1.2)

# With additional parameters
stretch_audio(
    input_path="speech.flac",
    output_path="slower_speech.wav", 
    ratio=1.4,
    sample_rate=22050,
    upper_freq=300
)
```

### Using the AudioStretch Class

For more control and advanced workflows:

```python
from audiostretchy import AudioStretch

# Initialize processor
processor = AudioStretch()

# Open input file
processor.open("input.mp3")

# Apply stretching
processor.stretch(ratio=1.1, upper_freq=350, lower_freq=60)

# Optional: resample
processor.resample(48000)

# Save result
processor.save("output.wav")
```

### Multiple Processing Steps

Process the same audio with different parameters:

```python
processor = AudioStretch()
processor.open("original.wav")

# Create slow version
processor.stretch(ratio=1.5)
processor.save("slow_version.wav")

# Reset and create fast version
processor.open("original.wav")  # Reload original
processor.stretch(ratio=0.7)
processor.save("fast_version.wav")
```

## Common Use Cases

### 1. Podcast Speed Adjustment

Speed up podcasts for faster listening:

```bash
# 1.25x speed (25% faster)
audiostretchy podcast.mp3 faster_podcast.mp3 --ratio 0.8
```

```python
stretch_audio("podcast.mp3", "faster_podcast.mp3", ratio=0.8)
```

### 2. Music Practice

Slow down music for practice:

```bash
# Make song 30% slower for learning
audiostretchy song.mp3 practice_version.wav --ratio 1.3
```

```python
stretch_audio("song.mp3", "practice_version.wav", ratio=1.3)
```

### 3. Voice Analysis

Stretch speech for detailed analysis:

```bash
# Slow down speech with speech-optimized settings
audiostretchy speech.wav analysis.wav --ratio 1.5 --upper_freq 300 --lower_freq 80
```

```python
stretch_audio(
    "speech.wav", 
    "analysis.wav", 
    ratio=1.5,
    upper_freq=300,
    lower_freq=80
)
```

### 4. Batch Processing

Process multiple files:

```python
import os
from audiostretchy import stretch_audio

input_dir = "input_files"
output_dir = "output_files"
ratio = 1.2

for filename in os.listdir(input_dir):
    if filename.endswith(('.mp3', '.wav', '.flac')):
        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, f"stretched_{filename}")
        
        stretch_audio(input_path, output_path, ratio=ratio)
        print(f"Processed: {filename}")
```

## Working with Different Formats

AudioStretchy supports many audio formats via Pedalboard:

### Input Formats

- **Uncompressed**: WAV, AIFF
- **Compressed**: MP3, FLAC, OGG, M4A
- **Professional**: BWF, RF64

### Output Format Selection

Format is determined by file extension:

```python
# Different output formats
processor.save("output.wav")    # WAV
processor.save("output.mp3")    # MP3  
processor.save("output.flac")   # FLAC
processor.save("output.ogg")    # OGG
```

### Format Conversion with Stretching

Combine format conversion with stretching:

```bash
# Convert MP3 to WAV while stretching
audiostretchy input.mp3 output.wav --ratio 1.1

# Convert to FLAC with resampling
audiostretchy input.wav output.flac --ratio 0.9 --sample_rate 48000
```

## Memory-Efficient Processing

For large files, AudioStretchy handles memory efficiently:

```python
# Large file processing
processor = AudioStretch()
processor.open("large_file.wav")
processor.stretch(ratio=1.2)
processor.save("stretched_large.wav")
# Memory is managed automatically
```

## Error Handling

Handle common issues gracefully:

```python
from audiostretchy import stretch_audio

try:
    stretch_audio("input.mp3", "output.wav", ratio=1.2)
    print("Success!")
except FileNotFoundError:
    print("Input file not found")
except Exception as e:
    print(f"Processing error: {e}")
```

## Performance Tips

### 1. Choose Appropriate Ratios

- **Normal range**: 0.5 - 2.0 (default)
- **Extended range**: 0.25 - 4.0 (use `--double_range true`)

### 2. Optimize for Content Type

**For speech:**
```bash
audiostretchy speech.wav output.wav --ratio 1.2 --upper_freq 300 --lower_freq 80
```

**For music:**
```bash
audiostretchy music.wav output.wav --ratio 1.1 --upper_freq 400 --lower_freq 50
```

### 3. Use Fast Mode for Quick Tests

```bash
audiostretchy test.wav output.wav --ratio 1.1 --fast_detection true
```

## Next Steps

Now that you're familiar with basic usage:

- **CLI Users**: See [Command Line Interface](03-cli-usage.md) for complete parameter reference
- **Python Developers**: Check [Python API](04-python-api.md) for advanced programming techniques  
- **Curious about internals**: Read [How It Works](05-how-it-works.md) to understand the TDHS algorithm

## Quick Reference

### Common Ratios

| Ratio | Effect | Use Case |
|-------|--------|----------|
| 0.5   | 2x faster | Quick review |
| 0.75  | 25% faster | Faster listening |
| 0.8   | 20% faster | Podcast speedup |
| 1.0   | No change | Testing/baseline |
| 1.2   | 20% slower | Learning audio |
| 1.5   | 50% slower | Detailed analysis |
| 2.0   | 2x slower | Transcription |

### File Extension Mapping

| Extension | Format | Quality | Use Case |
|-----------|--------|---------|----------|
| `.wav`    | WAV | Lossless | Professional |
| `.flac`   | FLAC | Lossless | Archival |
| `.mp3`    | MP3 | Lossy | General use |
| `.ogg`    | OGG | Lossy | Open source |
| `.m4a`    | AAC | Lossy | Apple ecosystem |