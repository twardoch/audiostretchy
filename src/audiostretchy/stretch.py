import wave # Keep for now, may be removed if pedalboard handles all aspects
from io import BytesIO
from pathlib import Path
from typing import BinaryIO, Optional, Union # Tuple removed

import numpy as np
import pedalboard
from pedalboard import Pedalboard, Resample # Explicit imports, removed AudioFile
from pedalboard import time_stretch as TimeStretch # Corrected import
from pedalboard.io import AudioFile as PedalboardAudioFile # Alias for clarity is correctly used

# Assuming TDHSAudioStretch might be conditionally used or replaced entirely.
# If fully replaced, this import and the vendors/stretch submodule might be removable later.
from .interface.tdhs import TDHSAudioStretch


class AudioStretch:
    """
    Main class to perform audio stretching operations using Pedalboard.
    """

    def __init__(self): # ext parameter removed as its usage was unclear and likely tied to old pcm handling
        """
        Constructor for the AudioStretch class.
        """
        self.nchannels = 1
        self.framerate = 44100 # Default, will be updated from file
        self.in_samples = None # Will be float32 numpy array
        self.samples = None    # Will be float32 numpy array, processed audio

    def open(
        self,
        path: Optional[Union[str, Path]] = None,
        file: Optional[BinaryIO] = None,
        # format parameter is largely handled by pedalboard by extension or content
    ):
        """
        Open an audio file using Pedalboard.

        Args:
            path (Union[str, Path], optional): Path to the audio file.
            file (BinaryIO, optional): Binary I/O object of the audio file.
        """
        input_source = file or path
        if not input_source:
            raise ValueError("Either path or file must be provided.")

        if isinstance(input_source, Path):
            input_source = str(input_source) # Pedalboard AudioFile expects str or file-like

        try:
            with PedalboardAudioFile(input_source) as f:
                self.in_samples = f.read(f.frames)
                self.framerate = f.samplerate
                self.nchannels = f.num_channels
            self.samples = self.in_samples.copy() # Start with a copy for processing
        except Exception as e:
            raise IOError(f"Could not open audio file {input_source}: {e}") from e


    def save(
        self,
        path: Optional[Union[str, Path]] = None,
        file: Optional[BinaryIO] = None,
        output_format: Optional[str] = None, # e.g., "wav", "mp3", "flac"
        # TODO: Add parameters for quality/bitrate for formats like MP3
    ):
        """
        Save the audio file using Pedalboard.

        Args:
            path (Union[str, Path], optional): Path to save the audio file.
            file (BinaryIO, optional): Binary I/O object to save the audio file.
            output_format (str, optional): The format of the audio file (e.g., 'wav', 'mp3').
                                       Pedalboard often infers from path extension.
        """
        output_target = file or path
        if not output_target:
            raise ValueError("Either path or file must be provided for saving.")

        if isinstance(output_target, Path):
            output_target = str(output_target) # Keep for error message if it fails before open

        if self.samples is None:
            raise ValueError("No audio data to save. Call open() and process first.")

        # self.samples is (num_channels, num_frames)
        # PedalboardAudioFile.write expects (num_channels, num_frames)
        processed_samples = self.samples

        # Ensure it's C-contiguous, especially if it might have been sliced or modified in ways that change flags.
        if not processed_samples.flags['C_CONTIGUOUS']:
            processed_samples = np.ascontiguousarray(processed_samples, dtype=np.float32)

        try:
            if isinstance(output_target, str) and not file: # If it's a path string
                with open(output_target, "wb") as actual_file_obj:
                    with PedalboardAudioFile(
                        actual_file_obj, # Pass the file object
                        mode="w",
                        samplerate=self.framerate,
                        num_channels=self.nchannels,
                        format=output_format if output_format else Path(output_target).suffix[1:]
                    ) as f:
                        f.write(processed_samples)
            elif file: # If it was a file object to begin with
                 with PedalboardAudioFile(
                    file, # Pass the original file object
                    mode="w",
                    samplerate=self.framerate,
                    num_channels=self.nchannels,
                    format=output_format
                ) as f:
                    f.write(processed_samples)
            else:
                # This case should ideally not be reached if output_target is always set
                raise ValueError("Invalid output target for saving.")

        except Exception as e:
            # Ensure output_target for the error message is the original path/file identifier
            error_location = path if path else (file.name if hasattr(file, 'name') else 'provided file object')
            raise IOError(f"Could not save audio file to {error_location}: {e}") from e

    # pcm_decode and pcm_encode are no longer needed as pedalboard handles this.
    # rms_level_dB might be needed for gap_ratio, or use pedalboard.Loudness

    def resample(self, target_framerate: int):
        """
        Resample the audio using Pedalboard.

        Args:
            target_framerate (int): Target framerate for resampling.
        """
        if self.samples is None:
            raise ValueError("No audio data to resample. Call open() first.")
        if target_framerate <= 0 or target_framerate == self.framerate:
            return # No resampling needed

        # Pedalboard processes audio block by block, best to create a board
        board = Pedalboard([
            Resample(
                target_sample_rate=target_framerate, # Corrected parameter name
                # quality="HQ" or "VHQ" can be set if desired, default is usually good
            )
        ])

        current_samples = self.samples # This is (channels, frames) at self.framerate

        board = Pedalboard([
            Resample(
                target_sample_rate=target_framerate,
                quality=pedalboard.Resample.Quality.Linear # Corrected case
            )
        ])

        # Process the audio through the board, providing the input sample rate.
        resampled_audio = board(current_samples, sample_rate=self.framerate)

        self.samples = resampled_audio

        self.framerate = target_framerate


    def stretch(
        self,
        ratio: float = 1.0, # This is inverse of pedalboard's stretch_factor
        # The following parameters are from TDHSAudioStretch and may not map directly
        # gap_ratio: float = 0.0,
        # upper_freq: int = 333,
        # lower_freq: int = 55,
        # buffer_ms: float = 25,
        # threshold_gap_db: float = -40,
        # double_range: bool = False, # TDHS specific range flag
        # fast_detection: bool = False, # TDHS specific quality/speed flag
        # normal_detection: bool = False, # TDHS specific quality/speed flag
        # ---- Pedalboard TimeStretch parameters ----
        # method: str = "auto" # e.g. "rubberband", "ola", "wsola" - "auto" usually picks rubberband if available
        # quality: str = "high" # e.g. "standard", "high", "extreme" for rubberband
    ):
        """
        Stretch the audio using Pedalboard.TimeStretch.
        Note: `ratio` > 1.0 extends audio (slower), < 1.0 shortens (faster).
        Pedalboard's `stretch_factor` is the inverse: factor > 1.0 is faster, < 1.0 is slower.

        Args:
            ratio (float): Original stretch ratio (compatible with TDHS definition).
                           > 1.0 makes audio longer, < 1.0 makes it shorter.
            # TODO: Map or implement gap_ratio and other features if possible.
            # TODO: Expose pedalboard.TimeStretch parameters like method, quality.
        """
        if self.samples is None:
            raise ValueError("No audio data to stretch. Call open() first.")
        if ratio == 1.0:
            return # No stretching needed

        # Convert audiostretchy ratio to pedalboard stretch_factor
        # ratio = 1.2 (20% longer) => pedalboard factor = 1/1.2 = 0.833...
        # ratio = 0.8 (20% shorter) => pedalboard factor = 1/0.8 = 1.25
        stretch_factor = 1.0 / ratio

        # For now, ignoring gap_ratio and other TDHS-specific params.
        # This is a simplified stretch of the whole audio.

        # Pedalboard's time_stretch is a direct function, not a plugin for the board.
        # It expects (num_channels, num_frames), which self.samples already is.
        current_samples_for_stretch = self.samples

        stretched_audio = TimeStretch(
            current_samples_for_stretch,
            samplerate=self.framerate,
            stretch_factor=stretch_factor,
            # TODO: Expose other parameters like high_quality, transient_mode etc.
        )

        # Output of time_stretch is (num_channels, num_frames).
        self.samples = stretched_audio

        # The number of frames and thus duration changes, framerate stays the same.


# Global function for CLI and simple library use
def stretch_audio(
    input_path: str,
    output_path: str,
    ratio: float = 1.0,
    # TDHS specific parameters - these will be ignored or need re-mapping for Pedalboard
    gap_ratio: float = 0.0, # Will be harder to implement with pedalboard directly
    upper_freq: int = 333,   # Not directly applicable to pedalboard.TimeStretch
    lower_freq: int = 55,    # Not directly applicable
    buffer_ms: float = 25,   # Not directly applicable
    threshold_gap_db: float = -40, # Not directly applicable for basic stretch
    double_range: bool = False,    # Not directly applicable
    fast_detection: bool = False,  # Not directly applicable (pedalboard has quality settings)
    normal_detection: bool = False,# Not directly applicable
    sample_rate: int = 0, # Target sample rate for resampling
):
    """
    Stretches the input audio file and saves the result to the output path using Pedalboard.

    Args:
        input_path (str): The path to the input audio file.
        output_path (str): The path to save the stretched audio file.
        ratio (float, optional): The stretch ratio. > 1.0 extends audio, < 1.0 shortens.
                                 Default is 1.0 (no change).
        sample_rate (int, optional): The target sample rate for resampling.
                                     Default is 0 (use sample rate of the input audio).

        NOTE: Parameters related to TDHS (gap_ratio, freq limits, etc.) are currently
              not supported in this Pedalboard-based version. The stretch applies uniformly.
    """
    audio_processor = AudioStretch()
    audio_processor.open(input_path)

    # 1. Stretch
    if ratio != 1.0:
        audio_processor.stretch(ratio=ratio) # Add other relevant params later if implemented

    # 2. Resample (if needed)
    if sample_rate > 0 and sample_rate != audio_processor.framerate:
        audio_processor.resample(target_framerate=sample_rate)

    audio_processor.save(output_path)
