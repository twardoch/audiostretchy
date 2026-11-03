---
this_file: src_docs/md/08-contributing.md
---
# Contributing

Use Python 3.10 or newer, `uv`, and a native C compiler. Windows developers need a Visual Studio developer shell.

```sh
uv sync --frozen
./test.sh
uv build
```

The tests cover mono/stereo audio, file and stream I/O, resampling, TDHS stretching, native compilation and release resumption. Add a regression test before changing behavior. Ruff handles linting and formatting.

The upstream source snapshot lives in `src/audiostretchy/_vendor/audio-stretch`; keep its files unmodified and update `UPSTREAM.md` when refreshing it. `c_interface/build.py` is the shared compiler for Hatch and development. Generated native libraries must not be committed.

Commit work before running `./publish.sh`. The script uses gitnextver and hatch-vcs to tag a release, waits for all GitHub platform wheels, and publishes the exact artifacts with uv. Use `./publish.sh --check` for local validation without creating a release. See the [release guide](https://github.com/twardoch/audiostretchy#releases).
