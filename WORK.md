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

Unrelated pre-existing src_docs/build.sh is left untracked. Legacy local submodule directories remain ignored; releases contain only the new source snapshot.
