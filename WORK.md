---
this_file: WORK.md
---
# Release modernization — 2026-11-03

Implemented the bundled upstream snapshot, shared native compiler, Hatch wheel hook, platform tags, five-platform GitHub Actions builds, hatch-vcs versioning, and uv-based release script using gitnextver 1.0.4.

Verification before release:
- Baseline: 55 existing tests passed.
- New tests reproduced missing-submodule build and invalid native input problems before fixes.
- ./test.sh: 64 passed; 88% coverage; Ruff lint and format checks passed.
- ./publish.sh --check: tests, sdist-to-wheel build, and strict Twine metadata checks passed.
- actionlint, shellcheck, and git diff --check passed.
- Distribution audit: one platform library per wheel; bundled sources byte-identical to the pinned upstream snapshot; sdist has source/build hook and no prebuilt libraries.
- Isolated installed macOS ARM wheel: real 0.9-ratio TDHS processing produced 39,689 samples from 44,100 input samples.
- macOS binary deployment target verified as 11.0; relocatable install name configured.

Pending live acceptance: GitHub's five native builds and Python endpoint tests, tag publication to PyPI, installation from PyPI on the user's machine, and requested MP3 conversion/duration measurement.

Unrelated pre-existing src_docs/build.sh is preserved and excluded locally through .git/info/exclude; gitnextver requires no visible untracked files. Legacy local submodule directories remain ignored; releases contain only the new source snapshot.

First live release v1.3.9: setup-uv has no v10 alias; switched to verified v10.3.3. No PyPI upload occurred. CI builds wheels on PR/manual runs and releases to avoid duplicate wheel builds for the branch and tag push.

Installed-wheel CI exposed cwd-relative legacy test fixtures (fixed to use __file__) and MSVC environment setup missing in the reusable wheel job (added). These failures occurred before any upload.

v1.3.10: four Unix platform wheels passed installed tests. Windows compiled/loaded and passed 63 project tests, but POSIX-only empty-argument quoting also collected cibuildwheel's intentional failure fixture. Switched to cross-platform `-o addopts=`. All six Python endpoint CI jobs passed. No upload occurred.
v1.3.11 was accidentally started before that config edit was applied; cancelled the redundant run. The corrected release will be v1.3.12.
