---
this_file: PLAN.md
---
# Release modernization

Bundle the current dbry/audio-stretch sources and build self-contained, platform-tagged wheels with Hatch. Keep the public Python API and use hatch-vcs as the only package version source.

- [x] Vendor upstream commit 0c8a4b8fc5ab569fa398f0f423e7cfe05be00efc, license and provenance; eliminate submodule build requirements.
- [x] Compile the bundled C library during wheel/editable builds using one shared builder; exclude old binaries and include source in wheel and sdist.
- [x] Validate native ABI, boundary failures, existing audio tests, wheel metadata, source archive rebuild and clean installed CLI.
- [x] Build/test wheels on GitHub Actions for Linux x86_64/aarch64, macOS x86_64/arm64 and Windows x86_64.
- [x] Automate semantic tags with gitnextver and hatch-vcs; publish exact CI artifacts using uv publish via ./publish.sh.
- [x] Update contributor/release docs and run the release pipeline, then verify PyPI artifacts and installation.

The release script requires committed work, main, uv and gh authentication. It selects the next semantic tag, pushes it, waits for CI, waits for publication and downloads the verified artifacts. The --check mode verifies local tests/builds without tagging or uploading. GitHub Actions owns uv publishing; the local command waits for its success and verifies downloaded artifacts. GitHub can also publish on tag pushes with its existing PyPI secret.
