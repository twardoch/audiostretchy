
import wave
import numpy as np
from pathlib import Path
from typing import Union, Tuple, BinaryIO
from .interface.tdhs import TDHSAudioStretch


class AudioStretch:
    def __init__(self):
        self.pcm = None
        self.nchannels = 1
        self.sampwidth = 2
        self.framerate = 44100
        self.nframes = 0
        self.in_samples = None
        self.samples = None

    def open_wav(self, path: Union[str, Path] = None, file: BinaryIO = None):
        if file: 
            wav = file
        elif path and Path(path).is_file(): 
            wav = str(path)
        with wave.open(wav, "rb") as wav_file:
            self.nchannels = wav_file.getnchannels()
            self.sampwidth = wav_file.getsampwidth()
            self.framerate = wav_file.getframerate()
            self.nframes = wav_file.getnframes()
            self.pcm = wav_file.readframes(self.nframes)
        self.pcm_decode()

    def save_wav(self, path: Union[str, Path] = None, file: BinaryIO = None):
        if file:
            wav = file
        elif path: 
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            wav = str(path)
        self.pcm_encode()
        with wave.open(wav, "wb") as wav_file:
            wav_file.setnchannels(self.nchannels)
            wav_file.setsampwidth(self.sampwidth)
            wav_file.setframerate(self.framerate)
            wav_file.writeframes(self.pcm)

    def pcm_decode(self):
        self.in_samples = np.frombuffer(self.pcm, dtype=np.int16)
        self.samples = self.in_samples

    def pcm_encode(self):
        self.pcm = self.samples.tobytes()

    def rms_level_dB(self, audio, samples, channels):
        rms_sum = 0.0

        for i in range(samples):
            if channels == 1:
                rms_sum += float(audio[i]) * audio[i]
            else:
                average = (audio[i * 2] + audio[i * 2 + 1]) / 2.0
                rms_sum += average * average

        return 10.0 * np.log10(rms_sum / samples / (32768.0 * 32767.0 * 0.5))

    def stretch_samples(
        self,
        ratio=1.0,
        gap_ratio=0.0,
        upper_freq=333,
        lower_freq=55,
        buffer_ms=25,
        threshold_gap_db=-40,
        dual_force=False,
        fast_detection=False,
        normal_detection=False,
    ):
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



def stretch_wav(
    input_wav,
    output_wav,
    ratio=1.0,
    gap_ratio=0.0,
    upper_freq=333,
    lower_freq=55,
    buffer_ms=25,
    threshold_gap_db=-40,
    dual_force=False,
    fast_detection=False,
    normal_detection=False,
):
    audio_stretch = AudioStretch()
    audio_stretch.open_wav(input_wav)
    audio_stretch.stretch_samples(
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
    audio_stretch.save_wav(output_wav)
