# AudioStretchy - TODO

## Deferred / bigger ideas

### Packaging & platforms
- [ ] **Windows support.** `c_interface/wrapper.py` looks for `interface/win/_stretch.dll`, but no DLL ships in `src/`. A stale `_stretch.dll` exists in the old committed `build/` tree; rebuild it cleanly from `audio-stretch` and add it, then restore the Windows classifier and CI leg.
- [ ] **Real per-platform wheels via cibuildwheel.** Today the wheel is a fat `py3-none-any` bundling every platform's binary. Building tagged wheels (one binary each) would be smaller and more correct.

### Code consolidation
- [ ] **Collapse the dual C-interface.** `interface/{mac,linux}/` holds the binaries actually loaded, while `c_interface/lib/_stretch_x64.so` is unused and `c_interface/build.py` writes to that unused path. Pick one layout: have `build.py` output to `interface/{platform}/`, drop `c_interface/lib/`, and remove `dummy.c`.
- [ ] **Wire `gap_ratio` through.** Several `stretch_audio` parameters (`gap_ratio`, `buffer_ms`, `threshold_gap_db`, `normal_detection`) are documented as "currently unused"; either implement silence-aware stretching or remove them.

### Testing
- [ ] Add a clean-room install test (install the built wheel in a fresh venv, run a real stretch).
- [ ] Add an end-to-end CLI smoke test (`audiostretchy in.wav out.wav --ratio 0.75`).

### Housekeeping
- [ ] After the release tag lands, untrack the committed `build/`, `dist/`, `test_env/`, and `llms.txt` (now git-ignored) in a dedicated cleanup commit.
