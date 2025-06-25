1.  **Project Setup and Initial Cleanup:**
    *   Create `PLAN.md` (this document) and `TODO.md` (linear checklist).
    *   Ensure `.gitignore` is comprehensive for build artifacts and IDE files.
    *   Review `AGENTS.md` (if any, none found at root yet) for specific instructions.

2.  **Core Logic Refactoring (`src/audiostretchy/stretch.py`):**
    *   **Modify `AudioStretch.stretch` method:**
        *   Ensure this method uses the `TDHSAudioStretch` class (from `src/audiostretchy/interface/tdhs.py`) for the time-stretching process.
        *   Remove or comment out the current implementation that uses `pedalboard.time_stretch`.
        *   The method should take audio data (as a NumPy array, float32, shape `(num_channels, num_frames)`) from `self.samples` (which is populated by `pedalboard` via the `open` method).
        *   Convert the float32 NumPy array to int16 NumPy array as expected by `TDHSAudioStretch`. This includes handling interleaving for stereo audio.
        *   Pass the appropriate parameters (ratio, frequency limits, flags) to `TDHSAudioStretch`.
        *   Convert the int16 output from `TDHSAudioStretch` back to float32 NumPy array and update `self.samples`. This includes de-interleaving for stereo.
    *   **Verify `AudioStretch.open` and `AudioStretch.save`:**
        *   Confirm these methods exclusively use `pedalboard.io.AudioFile` for all audio I/O operations (WAV, MP3, etc.). This seems mostly in place.
        *   Ensure they correctly handle file paths and file-like objects.
    *   **Verify `AudioStretch.resample`:**
        *   Confirm this method uses `pedalboard.Resample`. This also seems in place.
    *   **Review `stretch_audio` global function:**
        *   Ensure it correctly instantiates `AudioStretch` and calls its methods in the correct order (open, stretch, resample, save).
        *   Update its parameter list to accurately reflect the parameters used by the `TDHSAudioStretch`-based `AudioStretch.stretch` method. Parameters not used by `TDHSAudioStretch` (like pedalboard-specific ones) should be removed or clearly documented if they have a different purpose.

3.  **C Library Integration and Packaging (`pyproject.toml`, CI):**
    *   **Confirm Pre-compiled Library Strategy:** Stick with the current approach of pre-compiling the C shared libraries (`.so`, `.dylib`, `.dll`) via GitHub Actions and including them in the source distribution.
    *   **Verify `pyproject.toml` for Package Data:** Ensure `tool.setuptools.package-data` correctly includes the paths to these compiled libraries from `src/audiostretchy/interface/` subdirectories.
    *   **Verify `src/audiostretchy/interface/tdhs.py`:**
        *   Ensure `ctypes` bindings correctly load the platform-specific library.
        *   Double-check function signatures and data type conversions (e.g., `np.int16` to `ctypes.POINTER(ctypes.c_short)`).
    *   **Review GitHub Actions Workflow (`.github/workflows/ci.yaml`):**
        *   Confirm it correctly compiles `vendors/stretch/stretch.c` for all target platforms (Linux, macOS, Windows).
        *   Ensure it places the compiled artifacts in the correct locations within `src/audiostretchy/interface/` for packaging.
        *   Confirm the workflow commits these binaries back to the repository if changed.

4.  **Testing (`tests/test_stretch.py`):**
    *   **Expand Test Coverage:**
        *   Write comprehensive tests for the `AudioStretch` class methods (`open`, `save`, `stretch`, `resample`).
        *   Test with various audio formats (WAV, MP3 at minimum). Use `soundfile` or `pedalboard` to load reference/output files and verify properties (duration, sample rate, channel count, and potentially content similarity for non-stretching operations).
        *   Test different stretching ratios (e.g., `<1.0`, `1.0`, `>1.0`, and edge cases like `0.25`, `4.0` if `STRETCH_DUAL_FLAG` is used).
        *   Test `TDHSAudioStretch` parameters: `upper_freq`, `lower_freq`, `fast_detection`, `double_range`.
        *   Test behavior with mono and stereo files.
        *   Test resampling functionality thoroughly.
        *   Test the main `stretch_audio` function as an integration test.
    *   **Test Silence Handling (`gap_ratio`):**
        *   If the `gap_ratio` related parameters are intended to be effective, create specific tests with audio files containing clear silent and voiced segments to verify that silence is stretched differently. This might require creating or finding suitable test audio.
        *   If this feature is not fully implemented on the Python side (i.e., relies only on C library's internal capability without Python pre-segmentation), document this limitation clearly.
    *   **Test File-like Objects:** Add tests for opening from and saving to `io.BytesIO` objects.

5.  **Build and Publish Workflow:**
    *   **Verify Wheel Building:** After all changes, ensure `python -m build` (or `uv build`) successfully creates a wheel.
    *   **Inspect Wheel Contents:** Unzip the generated wheel and verify that the pre-compiled C libraries are included in the correct locations.
    *   **Test Installation from Wheel:** Install the generated wheel in a clean virtual environment and test the CLI and basic library import/usage.
    *   **"uv publish":** The goal is that `uv publish` would work. This mainly relies on a standard PEP 517 build and PyPI token configuration, which the existing `pypa/gh-action-pypi-publish` in `ci.yaml` handles for tagged releases.

6.  **Documentation:**
    *   Update `README.md` to reflect the refactored architecture, especially clarifying the roles of `pedalboard` (I/O, resampling) and the custom C library (stretching).
    *   Update any other relevant documentation (e.g., docstrings, API docs if generated).
    *   Ensure `PLAN.md` and `TODO.md` are accurate and complete.

7.  **Final Review and Submission:**
    *   Run all tests and ensure they pass.
    *   Run linters/formatters.
    *   Submit the changes with a clear commit message.
