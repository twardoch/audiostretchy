---
this_file: TODO.md
---
# Release tasks

- [x] Vendor upstream commit 0c8a4b8fc5ab569fa398f0f423e7cfe05be00efc, license and provenance; eliminate submodule build requirements.
- [x] Compile the bundled C library during wheel/editable builds using one shared builder; exclude old binaries and include source in wheel and sdist.
- [x] Validate native ABI, boundary failures, existing audio tests, wheel metadata, source archive rebuild and clean installed CLI.
- [ ] Build/test wheels on GitHub Actions for Linux x86_64/aarch64, macOS x86_64/arm64 and Windows x86_64.
- [ ] Automate semantic tags with gitnextver and hatch-vcs; publish exact CI artifacts using uv publish via ./publish.sh.
- [ ] Update contributor/release docs and run the release pipeline, then verify PyPI artifacts and installation.
