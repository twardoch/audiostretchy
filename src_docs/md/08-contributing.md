---
# this_file: src_docs/md/08-contributing.md
title: Contributing
description: Guidelines for contributing to the project
---

# Contributing

AudioStretchy welcomes contributions from the community! Whether you're fixing bugs, adding features, improving documentation, or sharing ideas, your help is appreciated.

## Getting Started

### Prerequisites

Before contributing, ensure you have:

- **Python 3.8+** installed
- **Git** for version control
- **C compiler** for building extensions (if modifying C code)
- **FFmpeg** for audio format support

### Setting Up Development Environment

#### 1. Fork and Clone

```bash
# Fork the repository on GitHub, then clone your fork
git clone https://github.com/YOUR_USERNAME/audiostretchy.git
cd audiostretchy

# Add upstream remote
git remote add upstream https://github.com/twardoch/audiostretchy.git
```

#### 2. Initialize Submodules

```bash
# The C library source is included as a submodule
git submodule update --init --recursive
```

#### 3. Create Virtual Environment

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### 4. Install Development Dependencies

```bash
# Install in editable mode with testing dependencies
pip install -e .[testing]

# Install pre-commit hooks
pre-commit install
```

### Development Tools

AudioStretchy uses several tools to maintain code quality:

| Tool | Purpose | Configuration |
|------|---------|---------------|
| **Black** | Code formatting | `pyproject.toml` |
| **isort** | Import sorting | `.isort.cfg` |
| **Flake8** | Linting | `pyproject.toml` |
| **pytest** | Testing | `pyproject.toml` |
| **pre-commit** | Git hooks | `.pre-commit-config.yaml` |

## Development Workflow

### 1. Create Feature Branch

```bash
# Always create a new branch for your changes
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b fix/issue-description
```

### 2. Make Changes

Follow these guidelines while developing:

#### Code Style

```python
# Follow PEP 8 and use type hints
def stretch_audio(
    input_path: str,
    output_path: str,
    ratio: float = 1.0,
    **kwargs: Any
) -> None:
    """
    Stretch audio file with specified ratio.
    
    Args:
        input_path: Path to input audio file
        output_path: Path for output file
        ratio: Stretch ratio (>1.0 = slower, <1.0 = faster)
        **kwargs: Additional stretching parameters
    """
    # Implementation here
    pass
```

#### Documentation

```python
class AudioStretch:
    """
    Audio time-stretching processor using TDHS algorithm.
    
    This class provides high-level interface for audio time-stretching
    without pitch changes. It uses the Time-Domain Harmonic Scaling
    algorithm for natural-sounding results.
    
    Example:
        Basic usage:
        
        >>> processor = AudioStretch()
        >>> processor.open("input.wav")
        >>> processor.stretch(ratio=1.2)
        >>> processor.save("output.wav")
    """
```

#### Error Handling

```python
def validate_ratio(ratio: float) -> None:
    """Validate stretch ratio parameter."""
    if not isinstance(ratio, (int, float)):
        raise TypeError(f"Ratio must be numeric, got {type(ratio)}")
    
    if ratio <= 0:
        raise ValueError(f"Ratio must be positive, got {ratio}")
    
    if ratio > 4.0 or ratio < 0.25:
        raise ValueError(f"Ratio {ratio} outside supported range (0.25-4.0)")
```

### 3. Write Tests

All new code should include tests:

#### Unit Tests

```python
# tests/test_stretch.py
import pytest
from audiostretchy import AudioStretch, stretch_audio

def test_ratio_validation():
    """Test ratio parameter validation."""
    with pytest.raises(ValueError, match="must be positive"):
        stretch_audio("input.wav", "output.wav", ratio=-1.0)

def test_basic_stretching():
    """Test basic audio stretching functionality."""
    # Create test audio or use fixtures
    stretch_audio("tests/data/test.wav", "tests/output/stretched.wav", ratio=1.2)
    
    # Validate output exists and has expected properties
    assert Path("tests/output/stretched.wav").exists()
```

#### Integration Tests

```python
def test_full_pipeline(tmp_path):
    """Test complete processing pipeline."""
    input_file = tmp_path / "input.wav"
    output_file = tmp_path / "output.wav"
    
    # Generate test audio
    create_test_audio(input_file, duration=2.0, sample_rate=44100)
    
    # Process
    stretch_audio(str(input_file), str(output_file), ratio=1.5)
    
    # Validate
    original_duration = get_audio_duration(input_file)
    stretched_duration = get_audio_duration(output_file)
    expected_duration = original_duration * 1.5
    
    assert abs(stretched_duration - expected_duration) < 0.1
```

### 4. Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src/audiostretchy --cov-report=term-missing

# Run specific test file
pytest tests/test_stretch.py

# Run specific test
pytest tests/test_stretch.py::test_ratio_validation
```

### 5. Check Code Quality

```bash
# Run all pre-commit hooks
pre-commit run --all-files

# Or run tools individually
black src/ tests/
isort src/ tests/
flake8 src/ tests/
```

### 6. Commit Changes

```bash
# Stage your changes
git add .

# Commit with descriptive message
git commit -m "feat: add support for streaming audio processing

- Implement StreamingAudioStretch class
- Add chunked processing for large files
- Include tests for streaming functionality
- Update documentation with streaming examples"
```

#### Commit Message Format

Use [Conventional Commits](https://www.conventionalcommits.org/) format:

- **feat**: New features
- **fix**: Bug fixes
- **docs**: Documentation changes
- **style**: Code style changes (formatting, etc.)
- **refactor**: Code refactoring
- **test**: Adding or updating tests
- **chore**: Maintenance tasks

### 7. Push and Create Pull Request

```bash
# Push to your fork
git push origin feature/your-feature-name

# Create pull request on GitHub
```

## Types of Contributions

### Bug Fixes

#### Finding Bugs

- Check the [issue tracker](https://github.com/twardoch/audiostretchy/issues)
- Test edge cases and unusual inputs
- Try different audio formats and parameters

#### Reporting Bugs

When reporting bugs, include:

```markdown
**Bug Description**
Clear description of the problem

**To Reproduce**
1. Steps to reproduce
2. Expected behavior
3. Actual behavior

**Environment**
- OS: [e.g., Windows 10, macOS 12, Ubuntu 20.04]
- Python version: [e.g., 3.9.7]
- AudioStretchy version: [e.g., 1.2.3]
- Audio file format: [e.g., MP3, WAV]

**Additional Context**
Error messages, logs, sample files (if possible)
```

#### Fixing Bugs

```python
# Example bug fix with test
def test_handles_empty_audio():
    """Test handling of empty audio files."""
    with pytest.raises(ValueError, match="empty audio"):
        stretch_audio("tests/data/empty.wav", "output.wav", ratio=1.2)

def load_audio_file(file_path):
    """Load audio file with empty file validation."""
    audio_data = pedalboard.load(file_path)
    
    if len(audio_data) == 0:
        raise ValueError(f"Audio file is empty: {file_path}")
    
    return audio_data
```

### New Features

#### Feature Requests

Before implementing new features:

1. **Check existing issues** for similar requests
2. **Create an issue** to discuss the feature
3. **Get feedback** from maintainers
4. **Design the API** before implementing

#### Feature Implementation

```python
# Example: Adding a quality assessment feature
class QualityAnalyzer:
    """Analyze audio quality after stretching."""
    
    def __init__(self):
        self.metrics = ['snr', 'thd', 'perceptual']
    
    def analyze(self, original: np.ndarray, stretched: np.ndarray) -> Dict[str, float]:
        """
        Analyze quality of stretched audio.
        
        Args:
            original: Original audio samples
            stretched: Stretched audio samples
            
        Returns:
            Dictionary of quality metrics
        """
        return {
            'snr': self._compute_snr(original, stretched),
            'thd': self._compute_thd(stretched),
            'perceptual': self._compute_perceptual_quality(original, stretched)
        }
```

### Documentation

#### Types of Documentation

1. **API Documentation**: Docstrings and type hints
2. **User Guides**: How-to guides and tutorials
3. **Examples**: Code examples and use cases
4. **Architecture**: Internal design documentation

#### Documentation Standards

```python
def stretch_audio(
    input_path: str,
    output_path: str,
    ratio: float = 1.0,
    **kwargs: Any
) -> None:
    """
    Stretch audio file without changing pitch.
    
    This function provides a simple interface for audio time-stretching
    using the TDHS (Time-Domain Harmonic Scaling) algorithm. The duration
    of the audio is changed while preserving the original pitch and timbre.
    
    Args:
        input_path: Path to the input audio file. Supports various formats
            including WAV, MP3, FLAC, OGG via Pedalboard library.
        output_path: Path where the stretched audio will be saved. Format
            is determined by file extension.
        ratio: Stretch ratio. Values > 1.0 make audio slower (longer),
            values < 1.0 make audio faster (shorter). Default is 1.0 (no change).
        **kwargs: Additional parameters passed to the TDHS algorithm.
            See Parameters section for details.
    
    Raises:
        FileNotFoundError: If input file doesn't exist.
        ValueError: If ratio is invalid or other parameter errors.
        RuntimeError: If processing fails.
    
    Example:
        Basic usage:
        
        >>> stretch_audio("input.mp3", "output.wav", ratio=1.2)
        
        Advanced usage with parameters:
        
        >>> stretch_audio(
        ...     "speech.wav", 
        ...     "slow_speech.wav",
        ...     ratio=1.5,
        ...     upper_freq=300,
        ...     lower_freq=80
        ... )
    
    Note:
        For processing multiple files or advanced control, consider using
        the AudioStretch class directly.
    """
```

### Performance Improvements

#### Profiling

```python
# Example profiling script
import cProfile
import pstats
from audiostretchy import stretch_audio

def profile_stretching():
    """Profile audio stretching performance."""
    pr = cProfile.Profile()
    pr.enable()
    
    # Run the code to profile
    stretch_audio("large_test_file.wav", "output.wav", ratio=1.2)
    
    pr.disable()
    
    # Analyze results
    stats = pstats.Stats(pr)
    stats.sort_stats('cumulative')
    stats.print_stats(20)  # Top 20 functions

if __name__ == "__main__":
    profile_stretching()
```

#### Optimization Example

```python
# Before: Inefficient memory usage
def process_large_file(audio_data, ratio):
    """Process large audio file."""
    # Load entire file into memory
    processed = stretch_algorithm(audio_data, ratio)
    return processed

# After: Memory-efficient chunked processing
def process_large_file_chunked(audio_data, ratio, chunk_size=8192):
    """Process large audio file in chunks."""
    output_chunks = []
    
    for i in range(0, len(audio_data), chunk_size):
        chunk = audio_data[i:i + chunk_size]
        processed_chunk = stretch_algorithm(chunk, ratio)
        output_chunks.append(processed_chunk)
        
        # Free memory explicitly for very large files
        del chunk
    
    return np.concatenate(output_chunks)
```

## C Library Development

### When to Modify C Code

Consider C library changes for:

- **Performance improvements**
- **New algorithm features**
- **Bug fixes in core processing**
- **Platform compatibility**

### C Development Setup

#### Prerequisites

=== "Linux"

    ```bash
    sudo apt-get install build-essential
    gcc --version  # Verify installation
    ```

=== "macOS"

    ```bash
    xcode-select --install
    clang --version  # Verify installation
    ```

=== "Windows"

    Install Visual Studio Build Tools or Visual Studio Community with C++ support.

#### Building C Library

```bash
# Navigate to C library source
cd vendors/stretch

# Compile for your platform
gcc -shared -fPIC -O3 stretch.c -o _stretch.so  # Linux
clang -shared -O3 stretch.c -o _stretch.dylib   # macOS
cl /LD /O2 stretch.c /Fe:_stretch.dll           # Windows

# Copy to appropriate interface directory
cp _stretch.so ../../src/audiostretchy/interface/linux/
```

#### Testing C Changes

```python
# Test C library changes
from audiostretchy.c_interface import TDHSAudioStretch

def test_c_library():
    """Test C library functionality."""
    processor = TDHSAudioStretch()
    
    # Test initialization
    context = processor.init(44100, 2, 1.2)
    assert context is not None
    
    # Test processing
    test_audio = np.random.randint(-32768, 32767, 1000, dtype=np.int16)
    result = processor.process(context, test_audio)
    
    assert len(result) > 0
    processor.cleanup(context)
```

## Release Process

### Version Management

AudioStretchy uses semantic versioning (SemVer):

- **Major** (X.0.0): Breaking changes
- **Minor** (0.X.0): New features (backward compatible)
- **Patch** (0.0.X): Bug fixes

### Creating a Release

```bash
# Ensure you're on main branch
git checkout main
git pull upstream main

# Run all tests
pytest
pre-commit run --all-files

# Build and test package
make build
make test

# Create release (maintainers only)
make release VERSION=1.3.0
```

### CI/CD Pipeline

The automated pipeline:

1. **Tests** on multiple Python versions and platforms
2. **Builds** wheels for all platforms
3. **Publishes** to PyPI on tag creation
4. **Updates** documentation

## Community Guidelines

### Code of Conduct

- Be respectful and inclusive
- Focus on constructive feedback
- Help newcomers get started
- Celebrate contributions of all sizes

### Getting Help

- **GitHub Issues**: Bug reports and feature requests
- **Discussions**: Questions and community help
- **Documentation**: Check existing docs first
- **Code Review**: Learn from feedback

### Recognition

Contributors are recognized through:

- **Contributors file**: Listed in CONTRIBUTORS.md
- **Release notes**: Mentioned in changelogs
- **GitHub**: Contributor statistics
- **Documentation**: Author attribution

## Advanced Topics

### Custom Algorithms

To implement alternative stretching algorithms:

```python
class CustomStretchAlgorithm:
    """Template for custom stretch algorithms."""
    
    def __init__(self):
        self.name = "custom_algorithm"
    
    def stretch(self, audio_data: np.ndarray, ratio: float) -> np.ndarray:
        """
        Implement your stretching algorithm here.
        
        Args:
            audio_data: Input audio samples
            ratio: Stretch ratio
            
        Returns:
            Stretched audio samples
        """
        # Your algorithm implementation
        pass
    
    def validate_parameters(self, **params) -> bool:
        """Validate algorithm-specific parameters."""
        pass
```

### Plugin System (Future)

Framework for extending AudioStretchy:

```python
# Future plugin interface
from audiostretchy.plugins import StretchPlugin

class PhaseVocoderPlugin(StretchPlugin):
    """Phase vocoder stretching plugin."""
    
    name = "phase_vocoder"
    supported_ratios = (0.1, 10.0)
    
    def stretch(self, audio_data, ratio, **params):
        """Phase vocoder implementation."""
        pass
```

### Real-time Processing (Future)

Considerations for real-time applications:

```python
class RealtimeAudioStretch:
    """Real-time audio stretching (future feature)."""
    
    def __init__(self, buffer_size=1024, latency_ms=50):
        self.buffer_size = buffer_size
        self.max_latency = latency_ms
        
    def process_chunk(self, audio_chunk):
        """Process audio in real-time chunks."""
        pass
```

## Questions?

If you have questions about contributing:

1. Check the [FAQ](09-api-reference.md#faq) in the API reference
2. Search [existing issues](https://github.com/twardoch/audiostretchy/issues)
3. Create a new [discussion](https://github.com/twardoch/audiostretchy/discussions)
4. Reach out to maintainers

Thank you for contributing to AudioStretchy! 🎵