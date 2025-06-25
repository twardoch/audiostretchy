# Plan for Streamlining AudioStretchy (Corrected)

This plan outlines the steps to streamline the `audiostretchy` library. The primary goal is to use the `dbry/audio-stretch` C library for core time-stretching functionality (including TDHS features like gap handling) and leverage the `pedalboard` library for robust audio I/O and resampling.

1.  **Revert Incorrect Changes to Restore C Library Focus:**
    *   Restore key source files (`src/audiostretchy/stretch.py`, `src/audiostretchy/interface/tdhs.py`, `.gitmodules`, `.github/workflows/ci.yaml`, `pyproject.toml`, `README.md`, `tests/test_stretch.py`) to a state that prioritizes the C library for stretching.
    *   Re-initialize submodules (`vendors/stretch`, `vendors/resample`) to ensure C library source code is present.
    *   Delete `PLAN.md`, `TODO.md`, `CHANGELOG.md` that were created under the incorrect premise of replacing the C library.
    *   *Status: Completed.*

2.  **Integrate `pedalboard` for Audio I/O and Resampling:**
    *   Modify `src/audiostretchy/stretch.py` to use `pedalboard.io.AudioFile` for all audio file reading and writing, replacing older methods (e.g., `wave` module, and removing the need for `pydub`, `pymp3`).
    *   Utilize `pedalboard.Resample` for audio resampling, removing the need for `soxr`.
    *   Ensure that the `AudioStretch.stretch` method correctly converts audio data between `pedalboard`'s float32 format and the C library's int16 PCM format.
    *   Update `pyproject.toml` to remove `pydub`, `pymp3`, and `soxr` as dependencies.
    *   *Status: Completed.*

3.  **Ensure Robust C Library Build and Packaging:**
    *   Verify that the CI workflow in `.github/workflows/ci.yaml` correctly checks out the `vendors/stretch` submodule and compiles the C library (`stretch.c`) for Linux, macOS, and Windows.
    *   Confirm that compiled libraries are placed in the correct `src/audiostretchy/interface/` subdirectories.
    *   Ensure `pyproject.toml` is configured via `tool.setuptools.package-data` to include these compiled libraries (`*.so`, `*.dylib`, `*.dll`) in the Python wheel.
    *   *Status: Completed.*

4.  **Update Documentation (`README.md`, etc.):**
    *   Accurately describe the architecture: `dbry/audio-stretch` C library for core TDHS time-stretching (including parameters like `gap_ratio`), and `pedalboard` for audio file I/O and resampling.
    *   Update installation instructions, detailing any build requirements for the C library if users build from source, and `pedalboard`'s own needs (e.g., FFmpeg for certain formats). Remove outdated `[all]` extras information.
    *   Ensure CLI and Python API examples in `README.md` are correct and reflect all relevant TDHS parameters.
    *   *Status: Completed.*

5.  **Update Tests (`tests/test_stretch.py`):**
    *   Ensure tests in `tests/test_stretch.py` thoroughly cover the C library's stretching functionalities using the Python wrapper, including various TDHS parameters (using defaults where specific variations are not tested).
    *   Verify that tests for `pedalboard`-based audio I/O (WAV, MP3) and resampling are adequate.
    *   *Status: Completed.*

6.  **Re-create `PLAN.md`, `TODO.md`, and `CHANGELOG.md`:**
    *   `PLAN.md`: This document.
    *   `TODO.md`: Simplified checklist version of this corrected plan.
    *   `CHANGELOG.md`: Summarize significant changes made, including the initial course correction.
    *   *Status: In Progress.*

7.  **Final Review and Submission:**
    *   Thoroughly review all code changes, documentation, and configuration.
    *   Ensure all tests pass.
    *   Submit the changes with a conventional commit message.
    *   *Status: Pending.*
