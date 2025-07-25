# this_file: src/audiostretchy/core.py
"""
Core AudioStretch class with Pedalboard I/O integration.
Provides high-level interface for audio time-stretching operations.
"""

from io import BytesIO
from pathlib import Path
from typing import BinaryIO, Optional, Union

import numpy as np
from pedalboard import Resample
from pedalboard.io import AudioFile

from .c_interface import TDHSAudioStretch


class AudioStretch:
    """
    High-level interface for audio time-stretching using TDHS algorithm.
    Uses Pedalboard for audio I/O and the audio-stretch C library for processing.
    """

    def __init__(self):
        """Initialize AudioStretch processor."""
        self.samples: Optional[np.ndarray] = None
        self.samplerate: int = 44100
        self.num_channels: int = 1
        
    def open(
        self,
        path: Optional[Union[str, Path]] = None,
        file: Optional[BinaryIO] = None,
        format: Optional[str] = None,
    ) -> None:
        """
        Open an audio file using Pedalboard.

        Args:
            path: Path to the audio file
            file: Binary I/O object containing audio data
            format: Audio format hint (usually inferred from extension)
        
        Raises:
            ValueError: If neither path nor file is provided
            IOError: If the file cannot be opened or read
        """
        if path is None and file is None:
            raise ValueError("Either path or file must be provided")
            
        input_source = file if file is not None else str(path)
        
        try:
            # Don't pass format when opening for reading from file path
            if isinstance(input_source, str):
                with AudioFile(input_source) as f:
                    # Read all audio data into memory
                    self.samples = f.read(f.frames)
                    self.samplerate = f.samplerate
                    self.num_channels = f.num_channels
            else:
                # For file-like objects, we might need format
                with AudioFile(input_source, format=format) as f:
                    # Read all audio data into memory
                    self.samples = f.read(f.frames)
                    self.samplerate = f.samplerate
                    self.num_channels = f.num_channels
                
        except Exception as e:
            source_desc = str(path) if path else "file object"
            raise IOError(f"Could not open audio file {source_desc}: {e}") from e

    def save(
        self,
        path: Optional[Union[str, Path]] = None,
        file: Optional[BinaryIO] = None,
        format: Optional[str] = None,
    ) -> None:
        """
        Save processed audio using Pedalboard.

        Args:
            path: Path to save the audio file
            file: Binary I/O object to write audio data
            format: Audio format (inferred from path extension if not specified)
            
        Raises:
            ValueError: If no audio data or invalid parameters
            IOError: If the file cannot be written
        """
        if path is None and file is None:
            raise ValueError("Either path or file must be provided")
            
        if self.samples is None:
            raise ValueError("No audio data to save. Call open() and process first")
            
        # Infer format from path extension if not specified
        if format is None and path is not None:
            format = Path(path).suffix.lstrip(".")
            
        try:
            if file is not None:
                # Use provided file object
                with AudioFile(
                    file,
                    mode="w",
                    samplerate=self.samplerate,
                    num_channels=self.num_channels,
                    format=format,
                ) as f:
                    f.write(self.samples)
            else:
                # Open file path for writing
                with open(str(path), 'wb') as fp:
                    with AudioFile(
                        fp,
                        mode="w",
                        samplerate=self.samplerate,
                        num_channels=self.num_channels,
                        format=format,
                    ) as f:
                        f.write(self.samples)
                
        except Exception as e:
            target_desc = str(path) if path else "file object"
            raise IOError(f"Could not save audio file to {target_desc}: {e}") from e

    def resample(self, target_framerate: int) -> None:
        """
        Resample audio to target sample rate using Pedalboard.

        Args:
            target_framerate: Target sample rate in Hz
            
        Raises:
            ValueError: If no audio data is loaded
        """
        if self.samples is None:
            raise ValueError("No audio data to resample. Call open() first")
            
        if target_framerate == self.samplerate:
            return  # No resampling needed
            
        resampler = Resample(target_sample_rate=target_framerate)
        self.samples = resampler(self.samples, sample_rate=self.samplerate)
        self.samplerate = target_framerate

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
        normal_detection: bool = False,
    ) -> None:
        """
        Stretch audio using the TDHS algorithm.

        Args:
            ratio: Stretch ratio (>1.0 = slower, <1.0 = faster)
            gap_ratio: Separate ratio for silent sections (0.0 = use main ratio)
            upper_freq: Upper frequency limit for period detection (Hz)
            lower_freq: Lower frequency limit for period detection (Hz)
            buffer_ms: Buffer size for silence detection (currently unused)
            threshold_gap_db: Silence threshold in dB (currently unused)
            double_range: Enable extended ratio range (0.25-4.0)
            fast_detection: Use faster period detection algorithm
            normal_detection: Force normal detection (currently unused)
            
        Raises:
            ValueError: If no audio data or invalid parameters
            RuntimeError: If stretching fails
            
        Note:
            gap_ratio, buffer_ms, threshold_gap_db are not currently implemented
            in this Python wrapper and require additional segmentation logic.
        """
        if self.samples is None:
            raise ValueError("No audio data to stretch. Call open() first")
            
        if ratio <= 0:
            raise ValueError("Stretch ratio must be positive")
            
        # Skip processing if no change needed
        effective_gap_ratio = gap_ratio if gap_ratio > 0 else ratio
        if ratio == 1.0 and effective_gap_ratio == 1.0:
            return
            
        # Convert float32 samples to int16 for C library
        samples_int16 = self._convert_to_int16(self.samples)
        
        # Set up TDHS parameters
        min_period = max(1, int(self.samplerate / upper_freq))
        max_period = int(self.samplerate / lower_freq)
        
        flags = 0
        if fast_detection:
            flags |= TDHSAudioStretch.STRETCH_FAST_FLAG
        if double_range or ratio < 0.5 or ratio > 2.0:
            flags |= TDHSAudioStretch.STRETCH_DUAL_FLAG
            
        # Initialize stretcher
        stretcher = TDHSAudioStretch(min_period, max_period, self.num_channels, flags)
        
        try:
            # Process audio
            output_samples = self._process_with_stretcher(stretcher, samples_int16, ratio)
            
            # Convert back to float32 and update samples
            self.samples = self._convert_from_int16(output_samples)
            
        finally:
            stretcher.deinit()

    def _convert_to_int16(self, samples: np.ndarray) -> np.ndarray:
        """Convert float32 samples to int16 format expected by C library."""
        # Clip to valid range and convert
        samples_clipped = np.clip(samples, -1.0, 1.0)
        samples_int16 = np.round(samples_clipped * 32767).astype(np.int16)
        
        # Interleave channels if stereo
        if self.num_channels == 1:
            return np.ascontiguousarray(samples_int16[0])
        elif self.num_channels == 2:
            # Interleave L,R,L,R...
            return np.ascontiguousarray(samples_int16.T.ravel())
        else:
            raise ValueError(f"Unsupported channel count: {self.num_channels}")

    def _convert_from_int16(self, samples_int16: np.ndarray) -> np.ndarray:
        """Convert int16 samples back to float32 format."""
        samples_float32 = samples_int16.astype(np.float32) / 32767.0
        
        # De-interleave channels if stereo
        if self.num_channels == 1:
            return samples_float32.reshape(1, -1)
        elif self.num_channels == 2:
            # De-interleave L,R,L,R... to (2, N)
            return samples_float32.reshape(-1, 2).T
        else:
            raise ValueError(f"Unsupported channel count: {self.num_channels}")

    def _process_with_stretcher(
        self, 
        stretcher: TDHSAudioStretch,
        samples_int16: np.ndarray,
        ratio: float
    ) -> np.ndarray:
        """Process samples using the TDHS stretcher."""
        num_input_frames = len(samples_int16) // self.num_channels
        
        # Calculate output buffer capacity
        max_ratio_for_capacity = 4.0 if ratio > 2.0 or ratio < 0.5 else 2.0
        effective_max_ratio = max(ratio, max_ratio_for_capacity if ratio > 1.0 else 1.0 / ratio)
        
        output_capacity = stretcher.output_capacity(num_input_frames, effective_max_ratio)
        output_buffer = np.zeros(output_capacity * self.num_channels, dtype=np.int16)
        
        # Process samples
        num_processed = stretcher.process_samples(
            samples_int16, num_input_frames, output_buffer, ratio
        )
        
        # Flush remaining samples
        flush_buffer = np.zeros(output_capacity * self.num_channels, dtype=np.int16)
        num_flushed = stretcher.flush(flush_buffer)
        
        # Combine processed and flushed samples
        total_samples = num_processed + num_flushed
        result = np.zeros(total_samples * self.num_channels, dtype=np.int16)
        
        processed_size = num_processed * self.num_channels
        flushed_size = num_flushed * self.num_channels
        
        result[:processed_size] = output_buffer[:processed_size]
        result[processed_size:processed_size + flushed_size] = flush_buffer[:flushed_size]
        
        return result


def stretch_audio(
    input_path: Union[str, Path],
    output_path: Union[str, Path],
    ratio: float = 1.0,
    gap_ratio: float = 0.0,
    upper_freq: int = 333,
    lower_freq: int = 55,
    buffer_ms: float = 25.0,
    threshold_gap_db: float = -40.0,
    double_range: bool = False,
    fast_detection: bool = False,
    normal_detection: bool = False,
    sample_rate: int = 0,
) -> None:
    """
    Convenience function to stretch an audio file.

    Args:
        input_path: Path to input audio file
        output_path: Path for output audio file
        ratio: Stretch ratio (>1.0 = slower, <1.0 = faster)
        gap_ratio: Separate ratio for silent sections (0.0 = use main ratio)
        upper_freq: Upper frequency limit for period detection (Hz)
        lower_freq: Lower frequency limit for period detection (Hz)
        buffer_ms: Buffer size for silence detection (currently unused)
        threshold_gap_db: Silence threshold in dB (currently unused)
        double_range: Enable extended ratio range (0.25-4.0)
        fast_detection: Use faster period detection algorithm
        normal_detection: Force normal detection (currently unused)
        sample_rate: Target sample rate for output (0 = keep original)
    """
    processor = AudioStretch()
    
    # Load audio
    processor.open(input_path)
    
    # Stretch audio
    processor.stretch(
        ratio=ratio,
        gap_ratio=gap_ratio,
        upper_freq=upper_freq,
        lower_freq=lower_freq,
        buffer_ms=buffer_ms,
        threshold_gap_db=threshold_gap_db,
        double_range=double_range,
        fast_detection=fast_detection,
        normal_detection=normal_detection,
    )
    
    # Resample if requested
    if sample_rate > 0 and sample_rate != processor.samplerate:
        processor.resample(sample_rate)
    
    # Save result
    processor.save(output_path)