import ctypes
import platform
from pathlib import Path

if platform.system() == 'Windows':
    lib_path = Path(__file__).parent / 'win' / '_stretch.dll'
elif platform.system() == 'Darwin':  # Mac
    lib_path = Path(__file__).parent / 'mac' / '_stretch.dylib'
elif platform.system() == 'Linux':  # Linux
    lib_path = Path(__file__).parent / 'linux' / '_stretch.so'
else:
    raise NotImplementedError("This platform is not supported.")

stretch_lib = ctypes.cdll.LoadLibrary(str(lib_path))


class Stretch:
    def __init__(self, shortest_period, longest_period, num_chans, flags):
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

    def output_capacity(self, max_num_samples, max_ratio):
        return self.stretch_output_capacity(self.handle, max_num_samples, max_ratio)

    def samples(self, samples, num_samples, output, ratio):
        return self.stretch_samples(self.handle, samples, num_samples, output, ratio)

    def flush(self, output):
        return self.stretch_flush(self.handle, output)

    def reset(self):
        self.stretch_reset(self.handle)

    def deinit(self):
        self.stretch_deinit(self.handle)
        self.handle = None
