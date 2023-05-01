import wave
import numpy as np
from pathlib import Path
from typing import Union, Tuple

from .interface.stretch import Stretch


def validate_ratio(ratio: float) -> float:
    """
    Validates the given ratio. It must be in the range [0.25, 4.0]

    :param ratio: The ratio to validate.
    :return: The validated ratio.
    :raises ValueError: If the ratio is not in the valid range.
    """
    if not (0.25 <= ratio <= 4.0):
        raise ValueError("Ratio must be from 0.25 to 4.0!")
    return ratio


def read_wave_file(filename: Union[str, Path]) -> Tuple:
    """
    Reads a wave file and returns its parameters and samples.

    :param filename: The path to the wave file.
    :return: A tuple containing the parameters and samples of the wave file.
    """
    filename = str(filename)  # convert to string if it's a Path object
    with wave.open(filename, "rb") as infile:
        params = infile.getparams()
        nchannels, sampwidth, framerate, nframes = params[:4]
        audio_data = infile.readframes(nframes)
        samples = np.frombuffer(audio_data, dtype=np.int16)

    return params, samples


def write_wave_file(filename: Union[str, Path], params, output_samples, num_samples):
    """
    Writes the output samples to a wave file.

    :param filename: The path to the output wave file.
    :param params: The parameters of the wave file.
    :param output_samples: The output samples to write.
    :param num_samples: The number of samples to write.
    """
    filename = str(filename)  # convert to string if it's a Path object
    with wave.open(filename, "wb") as outfile:
        outfile.setparams(params)
        outfile.writeframes(output_samples[:num_samples].tobytes())


def process_audio(
    infilename: Union[str, Path],
    outfilename: Union[str, Path],
    ratio: float = 1.0,
    silence_ratio: float = 0.0,
):
    """
    Processes an audio file.

    :param infilename: The path to the input audio file.
    :param outfilename: The path to the output audio file.
    :param ratio: The ratio to use for processing. Defaults to 1.0.
    :param silence_ratio: The silence ratio to use for processing. Defaults to 0.0.
    """
    ratio = validate_ratio(ratio)
    silence_ratio = silence_ratio or ratio
    silence_ratio = validate_ratio(silence_ratio)
    params, samples = read_wave_file(infilename)
    nchannels, sampwidth, framerate, nframes = params[:4]
    stretcher = Stretch(framerate // 333, framerate // 55, nchannels, 0)
    output_samples = np.zeros(stretcher.output_capacity(nframes, ratio), dtype=np.int16)
    num_samples = stretcher.samples(samples, len(samples), output_samples, ratio)
    num_samples += stretcher.flush(output_samples[num_samples:])
    write_wave_file(outfilename, params, output_samples, num_samples)

    stretcher.deinit()
