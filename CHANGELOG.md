# Changelog

## [Unreleased] - YYYY-MM-DD

### Architectural Changes
-   Re-focused the library to use David Bryant's `audio-stretch` C library (TDHS algorithm via `vendors/stretch` submodule) as the primary engine for time-stretching audio. This restores features like `gap_ratio` and other TDHS-specific tuning parameters.
-   Integrated the `spotify-pedalboard` library to handle audio file input/output (supporting formats like WAV, MP3, FLAC, OGG, etc.) and for audio resampling.

### Dependencies
-   `pedalboard` is now a core dependency.
-   Removed direct dependencies on `pydub`, `pymp3` (for MP3 handling) and `soxr` (for resampling), as these functionalities are now provided by `pedalboard`.

### Build Process
-   Restored and verified the CI workflow (`.github/workflows/ci.yaml`) for compiling the `audio-stretch` C library across Linux, macOS, and Windows.
-   Ensured `pyproject.toml` is correctly configured to package the pre-compiled C libraries into the Python wheels.

### API and CLI
-   The `AudioStretch` class and `stretch_audio` function in `audiostretchy.stretch` now expose parameters specific to the TDHS C library (e.g., `gap_ratio`, `upper_freq`, `lower_freq`, `double_range`, `fast_detection`).
-   **Note on `gap_ratio`**: While the parameters for detailed gap/silence processing (`gap_ratio`, `buffer_ms`, `threshold_gap_db`) are exposed to the Python interface, the current Python wrapper does not implement the per-segment audio analysis and differential ratio application performed by the original C command-line tool (`main.c`). The C library's core `stretch_samples` function receives a single ratio for the entire segment it processes. Effective `gap_ratio` behavior similar to the C CLI would require further development in the Python wrapper.

### Documentation
-   `README.md` updated to accurately reflect the current architecture, installation instructions (including `pedalboard`'s potential system dependencies like FFmpeg), and API usage with TDHS parameters.

### Testing
-   Tests in `tests/test_stretch.py` have been reviewed and confirmed to align with the C library for stretching (using default TDHS parameters in most test calls) and `pedalboard` for I/O and resampling.

*(Self-correction note: This changelog reflects the state after correcting an initial misinterpretation of the project goals, where `pedalboard` was incorrectly slated to replace the C library for stretching.)*
