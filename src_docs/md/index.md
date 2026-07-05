---
# this_file: src_docs/md/index.md
title: AudioStretchy Documentation
description: High-quality time-stretching of audio files without altering their pitch
---

# AudioStretchy Documentation

**AudioStretchy is a Python library and command-line interface (CLI) tool designed for high-quality time-stretching of audio files without altering their pitch.**

It leverages David Bryant's robust [audio-stretch C library](https://github.com/dbry/audio-stretch), which implements the Time-Domain Harmonic Scaling (TDHS) algorithm, particularly effective for speech. For versatile audio file handling (WAV, MP3, FLAC, OGG, etc.) and resampling, AudioStretchy integrates [Spotify's Pedalboard library](https://github.com/spotify/pedalboard).

## TL;DR

AudioStretchy provides high-quality audio time-stretching without pitch changes using the TDHS algorithm. Install with `pip install audiostretchy`, then use via CLI or Python API to stretch audio files while preserving natural sound quality.

## Table of Contents

### Getting Started
1. **[Installation](01-installation.md)** - How to install AudioStretchy and its dependencies
2. **[Quick Start](02-quick-start.md)** - Basic usage examples to get you up and running

### Usage Guides  
3. **[Command Line Interface](03-cli-usage.md)** - Complete CLI reference with examples
4. **[Python API](04-python-api.md)** - Programming interface for Python applications

### Technical Deep Dive
5. **[How It Works](05-how-it-works.md)** - Understanding the TDHS algorithm and processing pipeline
6. **[Core Architecture](06-core-architecture.md)** - Internal components and data flow
7. **[Parameters Reference](07-parameters-reference.md)** - Detailed parameter explanations and tuning

### Development
8. **[Contributing](08-contributing.md)** - Guidelines for contributing to the project
9. **[API Reference](09-api-reference.md)** - Complete API documentation with examples

## Key Features

- :material-music: **High-Quality Time Stretching** - TDHS algorithm preserves natural sound
- :material-file-music: **Wide Format Support** - WAV, MP3, FLAC, OGG, AIFF via Pedalboard
- :material-console-line: **Easy CLI Interface** - Simple command-line usage
- :material-language-python: **Python API** - Programmatic access for applications
- :material-laptop: **Cross-Platform** - Windows, macOS, and Linux support
- :material-tune: **Configurable Parameters** - Fine-tune stretching behavior

## Who Should Use This?

- **Musicians & Producers** - Adjust tempo without changing pitch
- **Audio Engineers** - Post-production timing adjustments  
- **Podcast/Video Editors** - Fit audio to specific durations
- **Developers** - Integrate time-stretching into applications
- **Researchers** - Explore audio processing techniques

## Quick Example

=== "Command Line"

    ```bash
    # Make audio 20% slower
    audiostretchy input.mp3 output.wav --ratio 1.2
    
    # Make audio 25% faster with custom parameters
    audiostretchy speech.wav faster.wav --ratio 0.75 --upper_freq 300
    ```

=== "Python"

    ```python
    from audiostretchy import stretch_audio
    
    # Simple stretching
    stretch_audio("input.mp3", "output.wav", ratio=1.2)
    
    # Advanced usage with class
    from audiostretchy import AudioStretch
    
    processor = AudioStretch()
    processor.open("input.flac")
    processor.stretch(ratio=0.8, upper_freq=350)
    processor.resample(48000)
    processor.save("output.wav")
    ```

## What Makes AudioStretchy Special?

Unlike simple playback speed changes that also alter pitch, AudioStretchy uses sophisticated algorithms to:

- **Preserve pitch** while changing duration
- **Maintain audio quality** through advanced signal processing
- **Handle various audio types** from speech to music
- **Provide fine control** over the stretching process

Ready to get started? Head to the [Installation](01-installation.md) guide!