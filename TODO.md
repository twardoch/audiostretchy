- [X] Create `PLAN.md`
- [ ] Create `TODO.md` (this file)
- [ ] Ensure `.gitignore` is comprehensive
- [ ] Review `AGENTS.md` (if any)

- [ ] **Core Logic Refactoring (`src/audiostretchy/stretch.py`):**
    - [ ] Modify `AudioStretch.stretch` to use `TDHSAudioStretch`
        - [ ] Remove/comment `pedalboard.time_stretch` usage
        - [ ] Input: float32 NumPy array from `self.samples`
        - [ ] Convert: float32 to int16 NumPy array (handle stereo interleaving)
        - [ ] Call `TDHSAudioStretch` with correct parameters
        - [ ] Convert: int16 output back to float32 NumPy array (handle stereo de-interleaving) and update `self.samples`
    - [ ] Verify `AudioStretch.open` (pedalboard, paths, file-like objects)
    - [ ] Verify `AudioStretch.save` (pedalboard, paths, file-like objects)
    - [ ] Verify `AudioStretch.resample` (pedalboard)
    - [ ] Review `stretch_audio` global function (parameters, method calls)

- [ ] **C Library Integration and Packaging (`pyproject.toml`, CI):**
    - [ ] Confirm pre-compiled library strategy (stick with current CI approach)
    - [ ] Verify `pyproject.toml` for `tool.setuptools.package-data` (includes compiled libs)
    - [ ] Verify `src/audiostretchy/interface/tdhs.py` (`ctypes` bindings, types)
    - [ ] Review GitHub Actions Workflow (`.github/workflows/ci.yaml`) (compilation, paths, commit)

- [ ] **Testing (`tests/test_stretch.py`):**
    - [ ] Expand test coverage for `AudioStretch` methods (`open`, `save`, `stretch`, `resample`)
    - [ ] Test various audio formats (WAV, MP3)
    - [ ] Test different stretching ratios (incl. edges)
    - [ ] Test `TDHSAudioStretch` parameters (`upper_freq`, `lower_freq`, `fast_detection`, `double_range`)
    - [ ] Test mono and stereo files
    - [ ] Test resampling thoroughly
    - [ ] Test `stretch_audio` function (integration)
    - [ ] Test silence handling (`gap_ratio`) - create specific audio files if needed
    - [ ] Test file-like objects for I/O

- [ ] **Build and Publish Workflow:**
    *   [ ] Verify `python -m build` (or `uv build`) creates wheel
    *   [ ] Inspect wheel contents (check for compiled C libs)
    *   [ ] Test installation from wheel in clean venv
    *   [ ] Confirm "uv publish" readiness (standard build, PyPI action)

- [ ] **Documentation:**
    - [ ] Update `README.md` (roles of pedalboard vs C library)
    - [ ] Update other docs (docstrings, API docs)
    - [ ] Ensure `PLAN.md` and `TODO.md` are accurate

- [ ] **Final Review and Submission:**
    - [ ] Run all tests (must pass)
    - [ ] Run linters/formatters
    - [ ] Submit changes (clear commit message)
