# this_file: tests/test_core.py
"""
Tests for the core AudioStretch functionality.
"""

import numpy as np
import pytest
from pathlib import Path

from audiostretchy.core import AudioStretch, stretch_audio


class TestAudioStretch:
    """Test cases for AudioStretch class."""
    
    def test_init(self):
        """Test AudioStretch initialization."""
        processor = AudioStretch()
        assert processor.samples is None
        assert processor.samplerate == 44100
        assert processor.num_channels == 1
    
    def test_open_missing_input(self):
        """Test error handling for missing input."""
        processor = AudioStretch()
        with pytest.raises(ValueError, match="Either path or file must be provided"):
            processor.open()
    
    def test_save_no_data(self):
        """Test error handling when saving without data."""
        processor = AudioStretch()
        with pytest.raises(ValueError, match="No audio data to save"):
            processor.save("output.wav")
    
    def test_stretch_no_data(self):
        """Test error handling when stretching without data."""
        processor = AudioStretch()
        with pytest.raises(ValueError, match="No audio data to stretch"):
            processor.stretch(1.2)
    
    def test_stretch_invalid_ratio(self):
        """Test error handling for invalid stretch ratio."""
        processor = AudioStretch()
        # Create dummy data
        processor.samples = np.random.random((1, 1000)).astype(np.float32)
        
        with pytest.raises(ValueError, match="Stretch ratio must be positive"):
            processor.stretch(0.0)
        
        with pytest.raises(ValueError, match="Stretch ratio must be positive"):
            processor.stretch(-1.0)
    
    def test_stretch_no_change(self):
        """Test that stretch with ratio 1.0 doesn't change audio."""
        processor = AudioStretch()
        original_samples = np.random.random((1, 1000)).astype(np.float32)
        processor.samples = original_samples.copy()
        processor.samplerate = 44100
        processor.num_channels = 1
        
        # Should return early without processing
        processor.stretch(1.0)
        
        # Samples should be unchanged
        np.testing.assert_array_equal(processor.samples, original_samples)
    
    def test_resample_no_data(self):
        """Test error handling when resampling without data."""
        processor = AudioStretch()
        with pytest.raises(ValueError, match="No audio data to resample"):
            processor.resample(48000)
    
    def test_resample_no_change(self):
        """Test that resampling to same rate doesn't change audio."""
        processor = AudioStretch()
        original_samples = np.random.random((1, 1000)).astype(np.float32)
        processor.samples = original_samples.copy()
        processor.samplerate = 44100
        processor.num_channels = 1
        
        # Should return early without processing
        processor.resample(44100)
        
        # Samples should be unchanged
        np.testing.assert_array_equal(processor.samples, original_samples)
    
    def test_convert_to_int16_mono(self):
        """Test float32 to int16 conversion for mono audio."""
        processor = AudioStretch()
        processor.num_channels = 1
        
        # Create test samples
        float_samples = np.array([[0.0, 0.5, -0.5, 1.0, -1.0]], dtype=np.float32)
        
        int16_samples = processor._convert_to_int16(float_samples)
        
        expected = np.array([0, 16384, -16384, 32767, -32767], dtype=np.int16)
        np.testing.assert_array_equal(int16_samples, expected)
    
    def test_convert_to_int16_stereo(self):
        """Test float32 to int16 conversion for stereo audio."""
        processor = AudioStretch()
        processor.num_channels = 2
        
        # Create test samples (2 channels, 3 frames)
        float_samples = np.array([
            [0.0, 0.5, -0.5],  # Left channel
            [1.0, -1.0, 0.0]   # Right channel
        ], dtype=np.float32)
        
        int16_samples = processor._convert_to_int16(float_samples)
        
        # Should be interleaved: L0, R0, L1, R1, L2, R2
        expected = np.array([0, 32767, 16384, -32767, -16384, 0], dtype=np.int16)
        np.testing.assert_array_equal(int16_samples, expected)
    
    def test_convert_from_int16_mono(self):
        """Test int16 to float32 conversion for mono audio."""
        processor = AudioStretch()
        processor.num_channels = 1
        
        int16_samples = np.array([0, 16383, -16384, 32767, -32767], dtype=np.int16)
        
        float_samples = processor._convert_from_int16(int16_samples)
        
        expected = np.array([[0.0, 16383/32767, -16384/32767, 1.0, -1.0]], dtype=np.float32)
        np.testing.assert_array_almost_equal(float_samples, expected, decimal=5)
    
    def test_convert_from_int16_stereo(self):
        """Test int16 to float32 conversion for stereo audio."""
        processor = AudioStretch()
        processor.num_channels = 2
        
        # Interleaved: L0, R0, L1, R1, L2, R2
        int16_samples = np.array([0, 32767, 16383, -32767, -16384, 0], dtype=np.int16)
        
        float_samples = processor._convert_from_int16(int16_samples)
        
        expected = np.array([
            [0.0, 16383/32767, -16384/32767],  # Left channel
            [1.0, -1.0, 0.0]                   # Right channel
        ], dtype=np.float32)
        np.testing.assert_array_almost_equal(float_samples, expected, decimal=5)
    
    def test_unsupported_channels(self):
        """Test error handling for unsupported channel counts."""
        processor = AudioStretch()
        processor.num_channels = 3  # Unsupported
        
        float_samples = np.random.random((3, 100)).astype(np.float32)
        
        with pytest.raises(ValueError, match="Unsupported channel count: 3"):
            processor._convert_to_int16(float_samples)
        
        int16_samples = np.random.randint(-32767, 32767, 300, dtype=np.int16)
        
        with pytest.raises(ValueError, match="Unsupported channel count: 3"):
            processor._convert_from_int16(int16_samples)


def test_stretch_audio_function():
    """Test the stretch_audio convenience function."""
    # This test would require actual audio files, so we'll just test the interface
    with pytest.raises(IOError):  # Should fail because file doesn't exist
        stretch_audio("nonexistent_input.wav", "output.wav", ratio=1.2)