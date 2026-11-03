---
this_file: src_docs/md/01-installation.md
---
# Installation

Use `uv tool install audiostretchy` for the CLI, or `uv add audiostretchy` in a Python project.

Python 3.10 or newer is required. Wheels include a native TDHS library for Linux x86_64/aarch64, macOS Intel/Apple Silicon (11+), and Windows x86_64. NumPy and Pedalboard install separately.

```sh
audiostretchy input.mp3 output.mp3 --ratio 0.9
```

To develop from source:

```sh
uv sync --frozen
./test.sh
uv build
```

A source build needs `cc` on Unix or a Visual Studio developer shell with `cl` on Windows. All required TDHS source is bundled; submodules and source downloads are unnecessary. Hatch compiles the library for wheels and editable installations.

See the [repository README](https://github.com/twardoch/audiostretchy#readme) for release commands and platform details.
