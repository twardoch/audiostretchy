---
# this_file: src_docs/md/04-python-api.md
title: Python API
description: Programming interface for Python applications
---

# Python API

AudioStretchy provides a comprehensive Python API for integrating time-stretching capabilities into your applications. This guide covers both simple function calls and advanced class-based usage.

## Quick Function Interface

### Basic Usage

The `stretch_audio` function provides the simplest way to process audio files:

```python
from audiostretchy import stretch_audio

# Basic stretching
stretch_audio("input.mp3", "output.wav", ratio=1.2)
```

### Function Signature

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

### Parameter Examples

```python
# Speech optimization
stretch_audio(
    "speech.wav", 
    "slow_speech.wav",
    ratio=1.3,
    upper_freq=300,
    lower_freq=80
)

# Music with high quality
stretch_audio(
    "song.flac",
    "practice.wav", 
    ratio=1.5,
    upper_freq=400,
    lower_freq=50,
    normal_detection=True
)

# Fast processing
stretch_audio(
    "podcast.mp3",
    "faster.mp3",
    ratio=0.8,
    fast_detection=True
)
```

## AudioStretch Class

For advanced control and multiple operations, use the `AudioStretch` class:

### Basic Class Usage

```python
from audiostretchy import AudioStretch

# Initialize processor
processor = AudioStretch()

# Open, process, save
processor.open("input.mp3")
processor.stretch(ratio=1.2)
processor.save("output.wav")
```

### Class Methods Overview

| Method | Purpose | Returns |
|--------|---------|---------|
| `open()` | Load audio file | None |
| `stretch()` | Apply time-stretching | None |
| `resample()` | Change sample rate | None |
| `save()` | Export processed audio | None |

### Advanced Class Usage

```python
processor = AudioStretch()

# Load file
processor.open("complex_audio.flac")

# Multiple processing steps
processor.stretch(
    ratio=1.1,
    upper_freq=350,
    lower_freq=60,
    double_range=True
)

# Optional resampling
processor.resample(48000)

# Save with explicit format
processor.save("processed.wav")
```

## File I/O Operations

### Opening Files

```python
# Simple file opening
processor.open("audio.mp3")

# With format specification (rare cases)
processor.open("audio_file", format="wav")
```

### Supported Input Formats

AudioStretchy supports numerous formats via Pedalboard:

- **Lossless**: WAV, FLAC, AIFF, BWF
- **Lossy**: MP3, OGG, M4A, AAC
- **Professional**: RF64, CAF

### Saving Files

```python
# Format determined by extension
processor.save("output.wav")    # WAV format
processor.save("output.mp3")    # MP3 format
processor.save("output.flac")   # FLAC format

# Explicit format specification
processor.save("output_file", format="ogg")
```

## Memory-Efficient Processing

### Working with BytesIO

For in-memory processing without file I/O:

```python
from io import BytesIO
from audiostretchy import AudioStretch

# Read audio data into memory
with open("input.mp3", "rb") as f:
    input_data = f.read()

# Process in memory
input_bio = BytesIO(input_data)
output_bio = BytesIO()

processor = AudioStretch()
processor.open(file=input_bio, format="mp3")
processor.stretch(ratio=1.2)
processor.save(file=output_bio, format="wav")

# Get processed data
processed_data = output_bio.getvalue()

# Save to file
with open("output.wav", "wb") as f:
    f.write(processed_data)
```

### Streaming Workflow

For large files or streaming applications:

```python
def process_audio_stream(input_stream, output_stream, ratio=1.0):
    """Process audio from input stream to output stream"""
    
    processor = AudioStretch()
    
    # Load from stream
    processor.open(file=input_stream, format="wav")
    
    # Process
    processor.stretch(ratio=ratio)
    
    # Save to stream
    processor.save(file=output_stream, format="wav")
    
    return output_stream
```

## Error Handling

### Common Exceptions

```python
from audiostretchy import stretch_audio

try:
    stretch_audio("input.mp3", "output.wav", ratio=1.2)
except FileNotFoundError:
    print("Input file not found")
except ValueError as e:
    print(f"Invalid parameter: {e}")
except RuntimeError as e:
    print(f"Processing error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Robust Error Handling

```python
import os
from pathlib import Path
from audiostretchy import AudioStretch

def safe_audio_stretch(input_path, output_path, **kwargs):
    """Safely stretch audio with comprehensive error handling"""
    
    # Validate input
    if not Path(input_path).exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")
    
    # Ensure output directory exists
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)
    
    processor = AudioStretch()
    
    try:
        # Process audio
        processor.open(input_path)
        processor.stretch(**kwargs)
        processor.save(output_path)
        
        return True
        
    except Exception as e:
        # Clean up partial output
        if Path(output_path).exists():
            Path(output_path).unlink()
        raise RuntimeError(f"Processing failed: {e}")

# Usage
try:
    safe_audio_stretch("input.mp3", "output.wav", ratio=1.2)
    print("Success!")
except Exception as e:
    print(f"Error: {e}")
```

## Batch Processing

### Simple Batch Processing

```python
import os
from pathlib import Path
from audiostretchy import stretch_audio

def batch_stretch(input_dir, output_dir, ratio=1.0, **kwargs):
    """Process all audio files in a directory"""
    
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Supported extensions
    audio_extensions = {'.mp3', '.wav', '.flac', '.ogg', '.m4a'}
    
    for file_path in input_path.iterdir():
        if file_path.suffix.lower() in audio_extensions:
            output_file = output_path / f"{file_path.stem}_stretched{file_path.suffix}"
            
            try:
                stretch_audio(str(file_path), str(output_file), ratio=ratio, **kwargs)
                print(f"✓ Processed: {file_path.name}")
            except Exception as e:
                print(f"✗ Failed: {file_path.name} - {e}")

# Usage
batch_stretch("input_files", "output_files", ratio=1.2, upper_freq=300)
```

### Advanced Batch Processing

```python
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import time

def process_single_file(file_info):
    """Process a single file with error handling"""
    input_file, output_file, params = file_info
    
    try:
        start_time = time.time()
        stretch_audio(str(input_file), str(output_file), **params)
        duration = time.time() - start_time
        
        return {
            'file': input_file.name,
            'status': 'success',
            'duration': duration
        }
    except Exception as e:
        return {
            'file': input_file.name,
            'status': 'error',
            'error': str(e)
        }

def parallel_batch_stretch(input_dir, output_dir, ratio=1.0, max_workers=4, **kwargs):
    """Process files in parallel for better performance"""
    
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Prepare file list
    audio_files = []
    audio_extensions = {'.mp3', '.wav', '.flac', '.ogg', '.m4a'}
    
    for file_path in input_path.iterdir():
        if file_path.suffix.lower() in audio_extensions:
            output_file = output_path / f"{file_path.stem}_stretched{file_path.suffix}"
            params = {'ratio': ratio, **kwargs}
            audio_files.append((file_path, output_file, params))
    
    # Process in parallel
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_file = {executor.submit(process_single_file, file_info): file_info[0] 
                         for file_info in audio_files}
        
        for future in as_completed(future_to_file):
            result = future.result()
            results.append(result)
            
            status_icon = "✓" if result['status'] == 'success' else "✗"
            if result['status'] == 'success':
                print(f"{status_icon} {result['file']} ({result['duration']:.1f}s)")
            else:
                print(f"{status_icon} {result['file']} - {result['error']}")
    
    return results

# Usage
results = parallel_batch_stretch(
    "input_files", 
    "output_files", 
    ratio=1.2, 
    max_workers=2,
    upper_freq=300
)

# Summary
successful = sum(1 for r in results if r['status'] == 'success')
print(f"\nProcessed {successful}/{len(results)} files successfully")
```

## Integration Patterns

### Flask Web Application

```python
from flask import Flask, request, send_file
from werkzeug.utils import secure_filename
import tempfile
import os

app = Flask(__name__)

@app.route('/stretch', methods=['POST'])
def stretch_audio_endpoint():
    """Web endpoint for audio stretching"""
    
    if 'audio' not in request.files:
        return {'error': 'No audio file provided'}, 400
    
    file = request.files['audio']
    ratio = float(request.form.get('ratio', 1.0))
    
    if file.filename == '':
        return {'error': 'No file selected'}, 400
    
    # Secure file handling
    filename = secure_filename(file.filename)
    
    with tempfile.TemporaryDirectory() as temp_dir:
        input_path = os.path.join(temp_dir, filename)
        output_path = os.path.join(temp_dir, f"stretched_{filename}")
        
        # Save uploaded file
        file.save(input_path)
        
        try:
            # Process audio
            stretch_audio(input_path, output_path, ratio=ratio)
            
            # Return processed file
            return send_file(output_path, as_attachment=True)
            
        except Exception as e:
            return {'error': str(e)}, 500

if __name__ == '__main__':
    app.run(debug=True)
```

### Django Integration

```python
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
import tempfile
import json

@csrf_exempt
def stretch_audio_view(request):
    """Django view for audio stretching"""
    
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    
    if 'audio' not in request.FILES:
        return JsonResponse({'error': 'No audio file'}, status=400)
    
    audio_file = request.FILES['audio']
    params = json.loads(request.POST.get('params', '{}'))
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # Save uploaded file
        input_path = os.path.join(temp_dir, audio_file.name)
        with open(input_path, 'wb') as f:
            for chunk in audio_file.chunks():
                f.write(chunk)
        
        # Process
        output_path = os.path.join(temp_dir, f"stretched_{audio_file.name}")
        
        try:
            stretch_audio(input_path, output_path, **params)
            
            # Return file
            with open(output_path, 'rb') as f:
                response = HttpResponse(f.read(), content_type='audio/wav')
                response['Content-Disposition'] = f'attachment; filename="stretched_{audio_file.name}"'
                return response
                
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
```

### CLI Wrapper

```python
import argparse
import sys
from pathlib import Path
from audiostretchy import stretch_audio

def create_cli():
    """Create a custom CLI wrapper"""
    
    parser = argparse.ArgumentParser(description='Custom AudioStretchy CLI')
    parser.add_argument('input', help='Input audio file')
    parser.add_argument('output', help='Output audio file')
    parser.add_argument('--ratio', type=float, default=1.0, help='Stretch ratio')
    parser.add_argument('--preset', choices=['speech', 'music', 'fast'], 
                       help='Parameter presets')
    
    return parser

def get_preset_params(preset):
    """Get predefined parameter sets"""
    presets = {
        'speech': {
            'upper_freq': 300,
            'lower_freq': 80,
            'normal_detection': True
        },
        'music': {
            'upper_freq': 400,
            'lower_freq': 50,
            'normal_detection': True
        },
        'fast': {
            'fast_detection': True
        }
    }
    return presets.get(preset, {})

def main():
    parser = create_cli()
    args = parser.parse_args()
    
    # Validate files
    if not Path(args.input).exists():
        print(f"Error: Input file '{args.input}' not found", file=sys.stderr)
        sys.exit(1)
    
    # Get parameters
    params = {'ratio': args.ratio}
    if args.preset:
        params.update(get_preset_params(args.preset))
    
    # Process
    try:
        stretch_audio(args.input, args.output, **params)
        print(f"Successfully processed: {args.input} -> {args.output}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
```

## Performance Optimization

### Memory Management

```python
import gc
from audiostretchy import AudioStretch

def memory_efficient_processing(files, ratio=1.0):
    """Process files with explicit memory management"""
    
    for input_file, output_file in files:
        processor = AudioStretch()
        
        try:
            processor.open(input_file)
            processor.stretch(ratio=ratio)
            processor.save(output_file)
        finally:
            # Explicit cleanup
            del processor
            gc.collect()
```

### Processing Time Estimation

```python
import time
from pathlib import Path

def estimate_processing_time(file_path, ratio=1.0):
    """Estimate processing time based on file size"""
    
    file_size_mb = Path(file_path).stat().st_size / (1024 * 1024)
    
    # Rough estimates (adjust based on your system)
    base_time = file_size_mb * 0.1  # seconds per MB
    ratio_factor = abs(ratio - 1.0) * 2 + 1  # ratio complexity
    
    estimated_time = base_time * ratio_factor
    
    return estimated_time

# Usage
estimated = estimate_processing_time("large_file.wav", ratio=1.5)
print(f"Estimated processing time: {estimated:.1f} seconds")
```

## Next Steps

- **Advanced Parameters**: Learn about [Parameters Reference](07-parameters-reference.md)
- **Algorithm Details**: Understand [How It Works](05-how-it-works.md)
- **Core Architecture**: Explore [Core Architecture](06-core-architecture.md)