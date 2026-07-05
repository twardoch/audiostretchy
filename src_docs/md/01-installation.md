---
# this_file: src_docs/md/01-installation.md
title: Installation
description: How to install AudioStretchy and its dependencies
---

# Installation

AudioStretchy can be installed in multiple ways depending on your needs. The package includes pre-compiled C extensions for cross-platform compatibility.

## Standard Installation

### Requirements

- Python 3.8 or higher
- pip package manager

### Quick Install

The simplest way to install AudioStretchy is via pip:

```bash
pip install audiostretchy
```

or with Python 3 explicitly:

```bash
python3 -m pip install audiostretchy
```

This installs AudioStretchy along with its core dependencies:

- **numpy** - For numerical operations
- **pedalboard** - For audio I/O and format support  
- **fire** - For the command-line interface

### Pre-compiled Wheels

AudioStretchy provides pre-compiled wheels for:

- **Windows** (x86_64)
- **macOS** (x86_64, ARM64)  
- **Linux** (x86_64)

These wheels include the compiled C extension, so no additional compilation is needed.

## FFmpeg Dependencies

For maximum audio format support, AudioStretchy relies on FFmpeg through the Pedalboard library.

!!! note "Format Support"
    Without FFmpeg, you'll be limited to basic formats like WAV. For MP3, M4A, OGG, and other compressed formats, FFmpeg is required.

### Installing FFmpeg

=== "macOS"

    Using Homebrew:
    ```bash
    brew install ffmpeg
    ```

=== "Ubuntu/Debian"

    Using apt:
    ```bash
    sudo apt-get update
    sudo apt-get install ffmpeg
    ```

=== "Windows"

    1. Download FFmpeg from [https://ffmpeg.org/download.html](https://ffmpeg.org/download.html)
    2. Extract the archive
    3. Add the `bin` directory to your system PATH

=== "Other Linux"

    Use your distribution's package manager:
    
    **CentOS/RHEL/Fedora:**
    ```bash
    sudo dnf install ffmpeg
    # or for older versions
    sudo yum install ffmpeg
    ```
    
    **Arch Linux:**
    ```bash
    sudo pacman -S ffmpeg
    ```

### Verifying FFmpeg Installation

Test FFmpeg installation:

```bash
ffmpeg -version
```

You should see version information if FFmpeg is properly installed.

## Development Installation

For contributing to AudioStretchy or working with the latest development version:

### Prerequisites

- Git
- Python 3.8+
- C compiler (GCC/Clang on Unix, MSVC on Windows)

### Clone and Install

```bash
# Clone the repository
git clone https://github.com/twardoch/audiostretchy.git
cd audiostretchy

# Initialize submodules (includes C library source)
git submodule update --init --recursive

# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in editable mode with development dependencies
pip install -e .[testing]
```

### Development Dependencies

The `[testing]` extra includes:

- **pytest** - Testing framework
- **pytest-cov** - Coverage reporting
- **black** - Code formatting
- **isort** - Import sorting
- **flake8** - Linting
- **pre-commit** - Git hooks

### Setting Up Pre-commit Hooks

```bash
pre-commit install
```

This ensures code quality checks run before each commit.

## Compiling C Extensions

If you modify the C library source in `vendors/stretch/`, you'll need to recompile:

### Prerequisites

=== "Linux"

    ```bash
    sudo apt-get install build-essential
    ```

=== "macOS"

    ```bash
    xcode-select --install
    ```

=== "Windows"

    Install Visual Studio Build Tools or Visual Studio Community with C++ support.

### Manual Compilation

The C library needs to be compiled into platform-specific shared libraries:

- **Linux**: `_stretch.so`
- **macOS**: `_stretch.dylib`  
- **Windows**: `_stretch.dll`

Place compiled libraries in the appropriate directories under `src/audiostretchy/interface/`.

!!! tip "CI Automation"
    The GitHub Actions workflow automatically handles compilation for official releases. See `.github/workflows/ci.yaml` for details.

## Virtual Environments

It's recommended to use virtual environments to avoid dependency conflicts:

### Using venv

```bash
python3 -m venv audiostretchy-env
source audiostretchy-env/bin/activate  # On Windows: audiostretchy-env\Scripts\activate
pip install audiostretchy
```

### Using conda

```bash
conda create -n audiostretchy python=3.11
conda activate audiostretchy
pip install audiostretchy
```

## Troubleshooting

### Common Issues

**Import errors after installation:**

```bash
python -c "import audiostretchy; print('Installation successful!')"
```

**Missing C extension:**

```
ImportError: cannot import name '_stretch' from 'audiostretchy.interface'
```

This usually means the C extension didn't compile properly. Try reinstalling or check platform compatibility.

**FFmpeg-related errors:**

```
RuntimeError: Could not open file for reading
```

Install FFmpeg as described above, or use WAV files which don't require FFmpeg.

**Permission errors on Windows:**

Run Command Prompt or PowerShell as Administrator.

### Platform-Specific Notes

=== "Apple Silicon (M1/M2)"

    AudioStretchy includes native ARM64 wheels for Apple Silicon Macs. No additional setup needed.

=== "Windows"

    Ensure you have the latest Visual C++ Redistributable installed if you encounter DLL errors.

=== "Linux"

    Most modern Linux distributions are supported. For older distributions, you may need to compile from source.

## Verification

Test your installation:

```bash
# Test CLI
audiostretchy --help

# Test Python import
python -c "from audiostretchy import stretch_audio; print('Success!')"

# Test with sample file (if you have audio files)
audiostretchy input.wav output.wav --ratio 1.1
```

Next: [Quick Start Guide](02-quick-start.md)