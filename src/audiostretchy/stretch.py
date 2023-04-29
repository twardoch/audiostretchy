import wave
import numpy as np
import fire

from .interface.stretch import Stretch

def validate_ratio(ratio):
    if not (0.25 <= ratio <= 4.0):
        raise ValueError("Ratio must be from 0.25 to 4.0!")
    return ratio


def read_wave_file(filename):
    with wave.open(filename, "rb") as infile:
        params = infile.getparams()
        nchannels, sampwidth, framerate, nframes = params[:4]
        audio_data = infile.readframes(nframes)
        samples = np.frombuffer(audio_data, dtype=np.int16)

    return params, samples


def write_wave_file(filename, params, output_samples, num_samples):
    with wave.open(filename, "wb") as outfile:
        outfile.setparams(params)
        outfile.writeframes(output_samples[:num_samples].tobytes())


def process_audio(infilename, outfilename, ratio=1.0, silence_ratio=0.0):
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


def main():
    fire.Fire(process_audio)


if __name__ == "__main__":
    main()
