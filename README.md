---
this_file: README.md
---
# AudioStretchy

Change audio duration without changing pitch, using David Bryant's
[audio-stretch](https://github.com/dbry/audio-stretch) TDHS engine.
Pedalboard reads and writes WAV, MP3, FLAC, OGG and AIFF; NumPy handles samples
and linear-interpolation resampling.

```sh
uv tool install audiostretchy
# 10% shorter, at the same pitch:
audiostretchy input.mp3 output.mp3 --ratio 0.9
```

For a Python project, use `uv add audiostretchy`:

```python
from audiostretchy import AudioStretch, stretch_audio

stretch_audio("input.wav", "output.wav", ratio=0.9)

processor = AudioStretch()
processor.open("input.wav")
processor.stretch(ratio=1.2)  # 20% longer
processor.resample(24000)
processor.save("output.wav")
```

Run `audiostretchy --help` for all parameters. Ratios from 0.25 to 4.0 are
supported; the extended range automatically cascades two TDHS instances.
Input must be mono or stereo. Stretching uses 16-bit PCM internally.
`gap_ratio`, `buffer_ms`, `threshold_gap_db`, and `normal_detection` remain
compatibility arguments: separate silence stretching is not implemented.

## Installation and platforms

Python 3.10 or newer. Published wheels contain one freshly compiled native
library and the corresponding C sources and license:

- Linux x86_64 and aarch64 (manylinux/glibc).
- macOS Intel and Apple Silicon (macOS 11 or newer).
- Windows x86_64.

The native library uses ctypes and is independent of the CPython ABI, so wheels
carry `py3-none-<platform>` tags. Dependencies install separately; NumPy and
Pedalboard are not copied into the wheel. Other platforms can build from the
source distribution when a C compiler and dependency wheels are available.
Linux musl and Windows ARM are not part of the tested wheel matrix.

All required TDHS source is bundled under `src/audiostretchy/_vendor/audio-stretch`.
There is no submodule initialization, build-time download, or compiler needed
when installing a compatible wheel. `UPSTREAM.md` records the pinned upstream
commit. Builds are reproducible from that snapshot; upstream is not fetched
implicitly during releases.

## Development

```sh
uv sync --frozen
./test.sh                # lint, format check and all tests
uvx hatch test          # alternative Hatch test environment
uv build                # sdist, then a native wheel built from that sdist
```

Building from source needs a C compiler (`cc` on Unix or MSVC `cl` on Windows).
On Windows run from a Visual Studio developer shell. The Hatch wheel hook and
`scripts/compile_c.py` share the same compiler implementation. Editable installs
compile the library too. `CC`, `CFLAGS`, and `LDFLAGS` are honoured on Unix;
`MACOSX_DEPLOYMENT_TARGET` defaults to 11.0 on macOS.

## Releases

`hatch-vcs` derives package versions from stable `vMAJOR.MINOR.PATCH` tags.
Untagged commits get a development version; source archives preserve their
version without needing a Git checkout.

After committing your changes on `main`:

```sh
./publish.sh --check     # tests + local builds + metadata checks; no release
./publish.sh             # auto patch version, push, CI builds, uv publish
./publish.sh minor       # choose a minor or major bump when appropriate
./publish.sh --resume v1.3.13  # resume the same release after fixing an external failure
```

The release command uses `uvx gitnextver` to create and atomically push the tag
and branch, waits for the Release workflow, downloads its exact artifacts, and
runs `uv publish`. GitHub Actions builds and tests all five platform wheels,
checks metadata, publishes with `uv publish`, and attaches the same files to the
GitHub release. Re-running upload is safe for identical files. It never silently
creates a new version when resuming a failed release.

Local prerequisites: `uv`, authenticated `gh`, Git push access, and PyPI upload
credentials if local upload is needed (`UV_PUBLISH_TOKEN`). GitHub uses the
repository secret `PYPI_TOKEN`; without it, configure a PyPI trusted publisher
for `release.yml`. Token values must stay out of files and command arguments.

The CI workflow also tests Python 3.10 and 3.14 on Linux, macOS and Windows and
builds the same five wheels on pull requests and manual runs.

## License

AudioStretchy wrapper: [BSD-3-Clause](LICENSE.txt). Bundled TDHS source:
David Bryant's BSD-style license in `_vendor/audio-stretch/license.txt`.
Pedalboard is a separate dependency licensed under GPLv3; consult its license
when distributing applications that use it.
