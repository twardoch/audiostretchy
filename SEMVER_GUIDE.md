---
this_file: SEMVER_GUIDE.md
---
# Semantic versions

`hatch-vcs` reads stable `vMAJOR.MINOR.PATCH` tags. `./publish.sh` uses `uvx gitnextver` for an automatic patch bump; pass `minor` or `major` for larger changes. It requires committed work on `main` and pushes the branch and tag atomically. Use `--resume vX.Y.Z` to retry the same release. See [README.md](README.md#releases).
