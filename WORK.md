---
this_file: WORK.md
---
# Verified release: v1.3.14 — 2026-11-03

All requested release work is complete.

- Upstream HEAD verified as `0c8a4b8fc5ab569fa398f0f423e7cfe05be00efc`; bundled C sources, header, CLI source, README, license and provenance. Windows checkouts preserve upstream LF bytes too.
- One shared builder compiles TDHS during Hatch wheel/editable builds. No submodule/download requirement, stale prebuilt libraries, or dummy extension remains in distributions.
- Five platform wheels built and tested: Linux x86_64/aarch64, macOS x86_64/arm64, Windows x86_64. Each contains one native library, correct platform metadata, and the exact upstream source.
- `hatch-vcs` supplies versions. `./publish.sh` used gitnextver 1.0.4 to tag/push v1.3.14, waited for GitHub Actions' `uv publish`, downloaded all six release assets, passed strict Twine checks, and exited 0. Local PyPI credentials are unnecessary.
- All six published PyPI SHA256 values match the downloaded release artifacts. Metadata and payload checks passed. Source archive includes the build hook, lockfile and Makefile, and no prebuilt binaries or private work log.
- Existing Python 3.13 system installation upgraded to v1.3.14 from its published PyPI wheel with SHA256 verification. Active CLI tested from outside the checkout: 0.90000774 duration ratio on a WAV test.
- Requested MP3 conversion ran immediately with ratio=0.9. Output decodes at 48 kHz stereo: ffprobe duration 9.116646 s; frame-padded duration 9.144 s. Original decoded input was 10.128 s. Audio was not manually auditioned.

## Verification

- Baseline: 55 existing tests passed before edits.
- Final ./test.sh: 64 passed, 88% branch-aware coverage; Ruff lint/format clean.
- Final source archive: ./test.sh passed all 64 tests without a Git checkout (89% statement coverage).
- Python 3.10 and 3.14 CI passed on Linux, macOS and Windows.
- Release workflow: all five wheel jobs, sdist job, metadata checks and PyPI publishing passed.
- actionlint, shellcheck and git diff --check passed.
- Documentation build passed. Deployment is opt-in through DEPLOY_DOCS=true after GitHub Pages is enabled.

Evidence: https://github.com/twardoch/audiostretchy/actions/runs/41573621840 and https://github.com/twardoch/audiostretchy/releases/tag/v1.3.14

## Release recovery notes

v1.3.9 exposed the missing setup-uv major alias, cwd-relative legacy fixtures, and missing MSVC environment. v1.3.10 exposed Windows shell quoting; redundant v1.3.11 was cancelled. None uploaded. v1.3.12 was published after repairing an expired GitHub token using local credentials without printing/storing values. v1.3.13 included source-archive/line-ending fixes. v1.3.14 removed redundant local upload to avoid PyPI index-propagation races; GitHub Actions owns publishing.

Pre-existing src_docs/build.sh is preserved and locally excluded through .git/info/exclude. Legacy local submodule directories are ignored and are not shipped.
