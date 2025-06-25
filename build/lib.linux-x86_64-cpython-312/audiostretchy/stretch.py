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
    Main class to perform audio processing.
    Uses Pedalboard for audio I/O (reading/writing various formats) and resampling.
    Uses a wrapped C library (TDHSAudioStretch) for the core time-stretching algorithm.
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
                        format=output_format or Path(output_target).suffix[1:]
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
            error_location = path or (file.name if hasattr(file, 'name') else 'provided file object')
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
        ratio: float = 1.0,
        gap_ratio: float = 0.0,
        upper_freq: int = 333,
        lower_freq: int = 55,
        buffer_ms: float = 25,
        threshold_gap_db: float = -40,
        double_range: bool = False,
        fast_detection: bool = False,
        normal_detection: bool = False,
    ):
        """
        Stretch the audio using the TDHS C library.
        Audio data is read as float32 by Pedalboard, converted to int16 for TDHS,
        and then converted back to float32.

        Args:
            ratio (float): Stretch ratio. > 1.0 makes audio longer. Default 1.0.
            gap_ratio (float): Stretch ratio for silence. Default 0.0 (uses main ratio).
            upper_freq (int): Upper frequency limit for period detection (Hz). Default 333.
            lower_freq (int): Lower frequency limit for period detection (Hz). Default 55.
            buffer_ms (float): Buffer size in milliseconds for silence detection. Default 25.
            threshold_gap_db (float): Silence threshold in dB. Default -40.
            double_range (bool): Use extended ratio range (0.25-4.0). Default False.
            fast_detection (bool): Use fast pitch detection. Default False.
            normal_detection (bool): Force normal pitch detection. Default False.
        """
        if self.samples is None:
            raise ValueError("No audio data to stretch. Call open() first.")

        if ratio == 1.0 and gap_ratio == 0.0: # Or gap_ratio == ratio
             # More precise check: if gap_ratio is effectively same as ratio
            effective_gap_ratio = gap_ratio if gap_ratio != 0.0 else ratio
            if ratio == 1.0 and effective_gap_ratio == 1.0:
                return # No stretching needed

        # Pedalboard samples are float32, shape (num_channels, num_frames)
        # TDHS C library expects int16, interleaved if stereo [L, R, L, R, ...]

        # Convert float32 samples to int16
        # Max value of int16 is 32767
        int16_samples = (self.samples * 32767).astype(np.int16)

        # Interleave if stereo
        if self.nchannels == 1:
            # For mono, TDHS expects a 1D array
            pcm_data_in = np.ascontiguousarray(int16_samples[0, :])
        elif self.nchannels == 2:
            # For stereo, interleave L and R channels
            pcm_data_in = np.ascontiguousarray(int16_samples.T.ravel())
        else:
            raise ValueError(f"TDHSAudioStretch currently supports 1 or 2 channels, not {self.nchannels}")

        flags = 0
        if fast_detection:
            flags |= TDHSAudioStretch.STRETCH_FAST_FLAG
        if double_range or ratio < 0.5 or ratio > 2.0 or \
           (gap_ratio != 0.0 and (gap_ratio < 0.5 or gap_ratio > 2.0)):
            flags |= TDHSAudioStretch.STRETCH_DUAL_FLAG

        # Note: normal_detection is implicitly handled by not setting STRETCH_FAST_FLAG
        # or if TDHS library itself defaults one way or another based on sample rate.
        # The original C CLI had logic for this. For simplicity, we rely on flags.

        min_period = int(self.framerate / upper_freq)
        max_period = int(self.framerate / lower_freq)

        stretcher = TDHSAudioStretch(min_period, max_period, self.nchannels, flags)

        # Determine buffer size for processing in chunks, esp. for gap_ratio
        # This logic mimics parts of the original C CLI application (main.c)
        # buffer_ms determines chunk size for analyzing silence vs. sound

        # If gap_ratio is not used, we can process in larger chunks or all at once
        # For simplicity in this Python wrapper, if gap_ratio is default (0.0),
        # we'll process the whole audio with the main `ratio`.
        # If gap_ratio is specified, we need a more complex loop segmenting audio.
        # The original AudioStretchy python code did not fully implement the C main.c's gap logic.
        # It passed all samples at once. We will replicate that simpler behavior first.
        # TODO: Re-evaluate implementing the more complex frame-by-frame silence detection from C if essential for MVP.
        # For now, if gap_ratio is set, it implies the C library might use it if it has internal logic,
        # but this Python wrapper isn't doing the pre-segmentation based on RMS levels like the C CLI.
        # The C library's `stretch_samples` itself doesn't take `gap_ratio`. It's the calling C code in `main.c`
        # that switches ratios based on RMS.
        # THEREFORE, `gap_ratio`, `buffer_ms`, `threshold_gap_db` from Python are not directly usable
        # by just calling `stretcher.process_samples` once with a single ratio.
        # The current TDHSAudioStretch python binding does not expose a way to set separate gap ratio.
        # This means `gap_ratio` and related params are effectively unused by the current Python bindings.
        # We will proceed by only using the main `ratio`.

        num_input_frames_per_channel = pcm_data_in.shape[0] // self.nchannels

        # Output capacity estimation
        # For dual flag, max_ratio can be 4.0, else 2.0
        max_effective_ratio_for_capacity = 4.0 if (flags & TDHSAudioStretch.STRETCH_DUAL_FLAG) else 2.0
        # If actual ratio is smaller, use that for a tighter bound
        max_effective_ratio_for_capacity = max(ratio, max_effective_ratio_for_capacity if ratio > 1.0 else 1.0/ratio if ratio !=0 else 1.0)


        out_capacity = stretcher.output_capacity(num_input_frames_per_channel, max_effective_ratio_for_capacity)
        pcm_data_out = np.zeros(out_capacity * self.nchannels, dtype=np.int16)

        num_processed_frames = stretcher.process_samples(
            pcm_data_in, num_input_frames_per_channel, pcm_data_out, ratio
        )

        # Flush any remaining samples
        # The flush buffer needs to be large enough.
        # Output_capacity should also cover typical flush sizes from TDHS.
        pcm_data_flush_out = np.zeros(out_capacity * self.nchannels, dtype=np.int16) # Re-use capacity estimate
        num_flushed_frames = stretcher.flush(pcm_data_flush_out)

        # Concatenate processed and flushed samples
        actual_output_samples_int16 = np.concatenate(
            (pcm_data_out[:num_processed_frames * self.nchannels],
             pcm_data_flush_out[:num_flushed_frames * self.nchannels])
        )

        stretcher.deinit()

        # Convert back to float32 and de-interleave
        # TDHS output is also int16, interleaved
        float32_output_samples = actual_output_samples_int16.astype(np.float32) / 32767.0

        if self.nchannels == 1:
            self.samples = float32_output_samples.reshape(1, -1)
        elif self.nchannels == 2:
            # De-interleave: reshape to (num_frames, num_channels) then transpose
            self.samples = float32_output_samples.reshape(-1, self.nchannels).T

        # Ensure contiguity for pedalboard processing later
        self.samples = np.ascontiguousarray(self.samples)


# Global function for CLI and simple library use
def stretch_audio(
    input_path: str,
    output_path: str,
    ratio: float = 1.0,
    gap_ratio: float = 0.0,
    upper_freq: int = 333,
    lower_freq: int = 55,
    buffer_ms: float = 25, # Currently not used effectively by Python stretch method
    threshold_gap_db: float = -40, # Currently not used effectively
    double_range: bool = False,
    fast_detection: bool = False,
    normal_detection: bool = False, # Currently not used effectively
    sample_rate: int = 0,
):
    """
    Stretches the input audio file using TDHS C library and saves the result.
    Uses Pedalboard for audio I/O and resampling.

    Args:
        input_path (str): Path to the input audio file.
        output_path (str): Path to save the stretched audio file.
        ratio (float, optional): Stretch ratio. > 1.0 extends audio. Default 1.0.
        gap_ratio (float, optional): Stretch ratio for silence. Default 0.0 (uses main ratio).
                                     NOTE: Effective use requires Python-side segmentation not yet implemented.
        upper_freq (int, optional): Upper frequency limit for period detection (Hz). Default 333.
        lower_freq (int, optional): Lower frequency limit (Hz). Default 55.
        buffer_ms (float, optional): Buffer size in ms for silence detection. Default 25. (Not currently used by Python)
        threshold_gap_db (float, optional): Silence threshold in dB. Default -40. (Not currently used by Python)
        double_range (bool, optional): Use extended ratio range (0.25-4.0). Default False.
        fast_detection (bool, optional): Use fast pitch detection. Default False.
        normal_detection (bool, optional): Force normal pitch detection. Default False. (Not currently used by Python)
        sample_rate (int, optional): Target sample rate for resampling. Default 0 (no resampling).
    """
    audio_processor = AudioStretch()
    audio_processor.open(input_path)

    # 1. Stretch
    # Note: gap_ratio, buffer_ms, threshold_gap_db, normal_detection are passed but may have limited effect
    # without Python-side audio segmentation logic for silence.
    audio_processor.stretch(
        ratio=ratio,
        gap_ratio=gap_ratio, # Passed to C, but C python wrapper doesn't use it for segmentation
        upper_freq=upper_freq,
        lower_freq=lower_freq,
        buffer_ms=buffer_ms,
        threshold_gap_db=threshold_gap_db,
        double_range=double_range,
        fast_detection=fast_detection,
        normal_detection=normal_detection
    )

    # 2. Resample (if needed)
    if sample_rate > 0 and sample_rate != audio_processor.framerate:
        audio_processor.resample(target_framerate=sample_rate)

    audio_processor.save(output_path)
