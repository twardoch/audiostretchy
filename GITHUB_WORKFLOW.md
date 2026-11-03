---
this_file: GITHUB_WORKFLOW.md
---
# GitHub workflows

`ci.yml` tests supported Python endpoints and calls `wheels.yml`. The reusable `wheels.yml` builds and tests five native platform wheels plus a source archive. `release.yml` runs on version tags, checks all artifacts, publishes with `uv publish` and creates a GitHub release.

Configure repository secret `PYPI_TOKEN` or a PyPI trusted publisher for `release.yml`. See [README.md](README.md#releases).
