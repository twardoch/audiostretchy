---
this_file: DEPENDENCIES.md
---
# Dependencies

- NumPy: sample conversion and interpolation.
- Pedalboard: audio decoding and encoding (GPLv3, installed separately).
- Fire: existing command-line API.
- hatchling and hatch-vcs: native wheel hook and version from Git tags.
- Bundled dbry/audio-stretch: TDHS engine, pinned in its UPSTREAM.md; BSD-style license.
- pytest, pytest-cov, soundfile: automated audio and build tests.
- Ruff: formatting and lint checks.
- cibuildwheel: five platform wheel builds and installed-wheel tests in CI.
- gitnextver 1.0.4: semantic tag selection and atomic push via uvx.
- Twine: distribution metadata checks via uvx.
- uv: dependency installation, isolated builds, and publishing.
