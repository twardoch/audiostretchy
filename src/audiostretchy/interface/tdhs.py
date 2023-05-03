"""
The _stretch library implements a time-stretching algorithm for audio signals. This algorithm modifies the length of the audio signal without changing its pitch. The code works by splitting the audio into small chunks or periods and then either repeating or removing some of these periods to alter the overall length of the audio. The original code works as follows.

1. The stretch_init function initializes a "stretching context" which contains all of the necessary information for the time stretching operation. This includes the audio data itself, the desired shortest and longest periods, the number of audio channels, and certain flags for adjusting the algorithm's behavior.

2. The stretch_samples function performs the actual time stretching. It works by iterating through the audio data, finding the best period to adjust based on the desired ratio, and then either repeating or removing that period to adjust the overall length of the audio.

3. The find_period and find_period_fast functions are used to find the best period in the audio data to adjust. They do this by calculating a correlation value for each possible period and then returning the period with the highest correlation. The correlation value is calculated based on the sum of the absolute differences of each corresponding pair of samples in the period.

4. The merge_blocks function is used to combine two audio periods into one. This is used when the algorithm needs to repeat a period to extend the length of the audio.

5. The stretch_flush function is used to output any remaining audio data after the time stretching operation is complete. This is necessary because the algorithm works by buffering a certain amount of audio data and then processing it in chunks.

6. Finally, the stretch_deinit function is used to free up any memory that was allocated during the time stretching operation.

This is a sophisticated algorithm for audio time stretching that is capable of producing high-quality results.

Below are ctypes bindings to the library.
"""

import ctypes
import platform
from pathlib import Path
import numpy as np

if platform.system() == 'Windows':
    lib_path = Path(__file__).parent / 'win' / '_stretch.dll'
elif platform.system() == 'Darwin':  # Mac
    lib_path = Path(__file__).parent / 'mac' / '_stretch.dylib'
elif platform.system() == 'Linux':  # Linux
    lib_path = Path(__file__).parent / 'linux' / '_stretch.so'
else:
    raise NotImplementedError("This platform is not supported.")

stretch_lib = ctypes.cdll.LoadLibrary(str(lib_path))


class TDHSAudioStretch:
    """
    The Stretch class is a Python binding for the _stretch library, providing an interface
    to time-stretch audio signals without changing their pitch.
    """
    STRETCH_FAST_FLAG = 0x1
    STRETCH_DUAL_FLAG = 0x2
    
    def __init__(self, shortest_period: int, longest_period: int, num_chans: int, flags: int) -> None:
        """
        Initialize the stretching context with the given parameters.

        :param shortest_period: The shortest period, affecting frequency handling.
        :param longest_period: The longest period, affecting frequency handling.
        :param num_chans: The number of audio channels.
        :param flags: Flags for adjusting the algorithm's behavior.
        """
        self.stretch_init = stretch_lib.stretch_init
        self.stretch_init.argtypes = [
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
        ]
        self.stretch_init.restype = ctypes.c_void_p
        self.handle = self.stretch_init(
            shortest_period, longest_period, num_chans, flags
        )
        self.stretch_output_capacity = stretch_lib.stretch_output_capacity
        self.stretch_output_capacity.argtypes = [
            ctypes.c_void_p,
            ctypes.c_int,
            ctypes.c_float,
        ]
        self.stretch_output_capacity.restype = ctypes.c_int
        self.stretch_samples = stretch_lib.stretch_samples
        self.stretch_samples.argtypes = [
            ctypes.c_void_p,
            np.ctypeslib.ndpointer(dtype=np.int16),
            ctypes.c_int,
            np.ctypeslib.ndpointer(dtype=np.int16),
            ctypes.c_float,
        ]
        self.stretch_samples.restype = ctypes.c_int
        self.stretch_flush = stretch_lib.stretch_flush
        self.stretch_flush.argtypes = [
            ctypes.c_void_p,
            np.ctypeslib.ndpointer(dtype=np.int16),
        ]
        self.stretch_flush.restype = ctypes.c_int
        self.stretch_reset = stretch_lib.stretch_reset
        self.stretch_reset.argtypes = [ctypes.c_void_p]
        self.stretch_reset.restype = None
        self.stretch_deinit = stretch_lib.stretch_deinit
        self.stretch_deinit.argtypes = [ctypes.c_void_p]
        self.stretch_deinit.restype = None

    def output_capacity(self, max_num_samples: int, max_ratio: float) -> int:
        """
        Determine the number of samples to reserve in the output array for
        stretch_samples() and stretch_flush().

        :param max_num_samples: The maximum number of samples.
        :param max_ratio: The maximum stretching ratio.
        :return: The number of samples to reserve in the output array.
        """
        return self.stretch_output_capacity(self.handle, max_num_samples, max_ratio)

    def process_samples(self, samples: np.ndarray, num_samples: int, output: np.ndarray, ratio: float) -> int:
        """
        Process the samples with a specified ratio.

        :param samples: The input audio samples.
        :param num_samples: The number of samples.
        :param output: The output audio samples.
        :param ratio: The stretching ratio.
        :return: The number of processed samples.
        """
        return self.stretch_samples(self.handle, samples, num_samples, output, ratio)

    def flush(self, output: np.ndarray) -> int:
        """
        Flush any leftover samples out at normal speed.

        :param output: The output audio samples.
        :return: The number of flushed samples.
        """
        return self.stretch_flush(self.handle, output)

    def reset(self) -> None:
        """
        Reset the stretching context.
        """
        self.stretch_reset(self.handle)

    def deinit(self) -> None:
        """
        Deinitialize the stretching context and free up memory.
        """
        self.stretch_deinit(self.handle)
        self.handle = None
