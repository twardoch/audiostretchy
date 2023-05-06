from wave import Wave_read, Wave_write
import wave
import numpy as np
from io import BytesIO
from pathlib import Path
from typing import Union, Tuple, BinaryIO, Optional
from .interface.tdhs import TDHSAudioStretch


class AudioStretch:
    """
    Class to perform audio stretching operations.
    """

    def __init__(self, ext: bool = False):
        """
        Constructor for the AudioStretch class.

        Args:
            ext (bool): external flag, defaults to False.
        """
        self.pcm = None
        self.nchannels = 1
        self.sampwidth = 2
        self.framerate = 44100
        self.nframes = 0
        self.in_samples = None
        self.samples = None
        self.ext = ext

    def open(
        self,
        path: Optional[Union[str, Path]] = None,
        file: Optional[BinaryIO] = None,
        format: Optional[str] = None,
    ):
        """
        Open an audio file.

        Args:
            path (Union[str, Path], optional): Path to the audio file.
            file (BinaryIO, optional): Binary I/O object of the audio file.
            format (str, optional): The format of the audio file.
        """
        format_ext = None
        audio_file = None
        if file:
            audio_file = file
        elif path:
            path = Path(path)
            if not path.is_file():
                raise FileNotFoundError(f"{str(path)} file not found")
            format_ext = path.suffix.lower()[1:]
            audio_file = open(path, "rb")
        if audio_file:
            if format == "mp3" or format_ext == "mp3":
                self.open_mp3(audio_file)
            elif format == "wav" or format_ext == "wav":
                self.open_wav(audio_file)

    def open_mp3(self, audio_file: BinaryIO):
        """
        Open a .mp3 audio file.

        Args:
            audio_file (BinaryIO): Binary I/O object of the audio file.
        """
        try:
            import mp3

            decoder = mp3.Decoder(audio_file)
            with open(BytesIO(), "wb") as wav_io:
                wav_file = Wave_write(wav_io)
                wav_file.setnchannels(decoder.get_channels())
                wav_file.setsampwidth(2)
                wav_file.setframerate(decoder.get_sample_rate())
                wav_file.writeframes(decoder.read())
            self.open_wav(wav_io)
        except ImportError:
            from pydub import AudioSegment

            audio = AudioSegment.from_file(audio_file, format="mp3")
            wav_io = BytesIO()
            audio.export(wav_io, format="wav")
            wav_io.seek(0)
            self.open_wav(wav_io)

    def open_wav(self, audio_file: BinaryIO):
        """
        Open a .wav audio file.

        Args:
            audio_file (BinaryIO): Binary I/O object of the audio file.
        """
        wav_file = Wave_read(audio_file)
        self.nchannels = wav_file.getnchannels()
        self.sampwidth = wav_file.getsampwidth()
        self.framerate = wav_file.getframerate()
        self.nframes = wav_file.getnframes()
        self.pcm = wav_file.readframes(self.nframes)
        wav_file.close()
        audio_file.close()
        self.pcm_decode()

    def save(
        self,
        path: Optional[Union[str, Path]] = None,
        file: Optional[BinaryIO] = None,
        format: Optional[str] = None,
    ):
        """
        Save the audio file.

        Args:
            path (Union[str, Path], optional): Path to save the audio file.
            file (BinaryIO, optional): Binary I/O object to save the audio file.
            format (str, optional): The format of the audio file.
        """
        format_ext = None
        audio_file = None
        if file:
            audio_file = file
        elif path:
            path = Path(path)
            format_ext = path.suffix.lower()[1:]
            audio_file = open(path, "wb")
        if audio_file:
            if format == "mp3" or format_ext == "mp3":
                self.save_mp3(audio_file)
            elif format == "wav" or format_ext == "wav":
                self.save_wav(audio_file)

    def save_mp3(self, audio_file: BinaryIO, bit_rate: int = 128, quality: int = 5):
        """
        Save the audio file in .mp3 format.

        Args:
            audio_file (BinaryIO): Binary I/O object to save the audio file.
            bit_rate (int): Bit rate of the audio file.
            quality (int): Quality of the audio file.
        """
        self.pcm_encode()
        try:
            import mp3

            encoder = mp3.Encoder(audio_file)
            encoder.set_bit_rate(bit_rate)
            encoder.set_sample_rate(self.framerate)
            encoder.set_channels(self.nchannels)
            encoder.set_quality(quality)
            encoder.set_mod(
                mp3.MODE_STEREO if nchannels == 2 else mp3.MODE_SINGLE_CHANNEL
            )
            encoder.write(self.pcm)
        except ImportError:
            from pydub import AudioSegment

            wav_io = BytesIO()
            self.save_wav(wav_io, close=False)
            wav_io.seek(0)
            audio = AudioSegment.from_file(wav_io, format="wav")
            wav_io.close()
            audio.export(audio_file, format="mp3", bitrate=f"{bit_rate}k")

    def save_wav(self, audio_file: BinaryIO, close: bool = True):
        """
        Save the audio file in .wav format.

        Args:
            audio_file (BinaryIO): Binary I/O object to save the audio file.
            close (bool): Flag to close the audio file after saving. Defaults to True.
        """
        self.pcm_encode()
        wav_file = Wave_write(audio_file)
        wav_file.setnchannels(self.nchannels)
        wav_file.setsampwidth(self.sampwidth)
        wav_file.setframerate(self.framerate)
        wav_file.writeframes(self.pcm)
        if not close:
            return wav_file
        wav_file.close()
        audio_file.close()
        return True

    def pcm_decode(self):
        """
        Decode PCM audio data.
        """
        self.in_samples = np.frombuffer(self.pcm, dtype=np.int16)
        self.samples = self.in_samples

    def pcm_encode(self):
        """
        Encode audio data to PCM.
        """
        self.pcm = self.samples.tobytes()

    def rms_level_dB(self, audio: np.ndarray, samples: int, channels: int) -> float:
        """
        Calculate the Root Mean Square (RMS) level in decibels (dB).

        Args:
            audio (np.ndarray): Audio data.
            samples (int): Number of samples.
            channels (int): Number of audio channels.

        Returns:
            float: RMS level in dB.
        """
        rms_sum = 0.0

        for i in range(samples):
            if channels == 1:
                rms_sum += float(audio[i]) * audio[i]
            else:
                average = (audio[i * 2] + audio[i * 2 + 1]) / 2.0
                rms_sum += average * average

        return 10.0 * np.log10(rms_sum / samples / (32768.0 * 32767.0 * 0.5))

    def resample(self, framerate: int):
        """
        Resample the audio.

        Args:
            framerate (int): Target framerate for resampling.
        """
        if framerate > 0 and framerate != self.framerate:
            import soxr

            self.samples = soxr.resample(
                self.samples, self.framerate, framerate, quality="VHQ"
            )
            self.framerate = framerate

    def stretch(
        self,
        ratio: float = 1.0,
        gap_ratio: float = 0.0,
        upper_freq: int = 333,
        lower_freq: int = 55,
        buffer_ms: float = 25,
        threshold_gap_db: float = -40,
        dual_force: bool = False,
        fast_detection: bool = False,
        normal_detection: bool = False,
    ):
        """
        Stretch the audio.

        Args:
            ratio (float): Stretch ratio. Defaults to 1.0.
            gap_ratio (float): Gap ratio. Defaults to 0.0.
            upper_freq (int): Upper frequency limit. Defaults to 333.
            lower_freq (int): Lower frequency limit. Defaults to 55.
            buffer_ms (float): Buffer size in milliseconds. Defaults to 25.
            threshold_gap_db (float): Threshold gap in dB. Defaults to -40.
            dual_force (bool): Flag for dual force. Defaults to False.
            fast_detection (bool): Flag for fast detection. Defaults to False.
            normal_detection (bool): Flag for normal detection. Defaults to False.
        """
        gap_ratio = gap_ratio or ratio
        flags = 0
        silence_mode = gap_ratio and gap_ratio != ratio
        buffer_samples = int(self.framerate * (buffer_ms / 1e3))
        min_period = self.framerate // upper_freq
        max_period = self.framerate // lower_freq
        max_ratio = ratio

        if (
            dual_force
            or ratio < 0.5
            or ratio > 2.0
            or (silence_mode and (gap_ratio < 0.5 or gap_ratio > 2.0))
        ):
            flags |= TDHSAudioStretch.STRETCH_DUAL_FLAG

        if (fast_detection or self.framerate >= 32000) and not normal_detection:
            flags |= TDHSAudioStretch.STRETCH_FAST_FLAG

        stretcher = TDHSAudioStretch(min_period, max_period, self.nchannels, flags)

        if silence_mode:
            non_silence_frames = 0
            silence_frames = 0
            consecutive_silence_frames = 1
            self.samples = np.zeros(
                stretcher.output_capacity(self.nframes, max_ratio), dtype=np.int16
            )
            num_samples = 0

            for idx in range(0, len(self.in_samples), buffer_samples):
                chunk = self.in_samples[idx : idx + buffer_samples]
                chunk_size = len(chunk)
                level = self.rms_level_dB(chunk, chunk_size, self.nchannels)

                if level > threshold_gap_db:
                    consecutive_silence_frames = 0
                    non_silence_frames += 1
                else:
                    consecutive_silence_frames += 1
                    silence_frames += 1

                current_ratio = gap_ratio if consecutive_silence_frames >= 3 else ratio
                num_samples += stretcher.process_samples(
                    chunk, chunk_size, self.samples[num_samples:], current_ratio
                )

        else:
            self.samples = np.zeros(
                stretcher.output_capacity(self.nframes, ratio), dtype=np.int16
            )
            num_samples = stretcher.process_samples(
                self.in_samples, len(self.in_samples), self.samples, ratio
            )

        num_samples += stretcher.flush(self.samples[num_samples:])
        stretcher.deinit()


def stretch_audio(
    input_path: str,
    output_path: str,
    ratio: float = 1.0,
    gap_ratio: float = 0.0,
    upper_freq: int = 333,
    lower_freq: int = 55,
    buffer_ms: float = 25,
    threshold_gap_db: float = -40,
    dual_force: bool = False,
    fast_detection: bool = False,
    normal_detection: bool = False,
    sample_rate: int = 0,
    ):
    """Stretches the input audio file and saves the result to the output path.

Args:
    input_path (str): The path to the input WAV or MP3 audio file.
    output_path (str): The path to save the stretched WAV or MP3 audio file.
    ratio (float, optional): The stretch ratio, where values greater than 1.0
        will extend the audio and values less than 1.0 will shorten the audio.
        Default is 1.0 = no stretching.
    gap_ratio (float, optional): The stretch ratio for gaps (silence) in the audio.
        Default is 0.0 = use ratio.
    upper_freq (int, optional): The upper frequency limit for period detection in Hz.
        Default is 333 Hz.
    lower_freq (int, optional): The lower frequency limit. Default is 55 Hz.
    buffer_ms (float, optional): The buffer size in milliseconds for processing
        the audio in chunks. Default is 25 ms.
    threshold_gap_db (float, optional): The threshold level in dB to
        determine if a section of audio is considered a gap (silence). Default is -40 dB.
    dual_force (bool, optional): If True, forces the algorithm to operate in
        dual-force mode, which may improve the quality of the stretched audio
        but may also increase processing time. 
    fast_detection (bool, optional): If True, enables fast period detection,
        which may speed up processing but reduce the quality of the stretched
        audio. 
    normal_detection (bool, optional): If True, forces the algorithm to use
        normal period detection instead of fast period detection.
    sample_rate (int, optional): The target sample rate for resampling the stretched audio in Hz. Default is 0 = use sample rate of the input audio.
"""
    audio_stretch = AudioStretch()
    audio_stretch.open(input_path)
    audio_stretch.stretch(
        ratio,
        gap_ratio,
        upper_freq,
        lower_freq,
        buffer_ms,
        threshold_gap_db,
        dual_force,
        fast_detection,
        normal_detection,
    )
    audio_stretch.resample(sample_rate)
    audio_stretch.save(output_path)
