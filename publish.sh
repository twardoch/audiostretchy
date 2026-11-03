#!/usr/bin/env bash
# this_file: publish.sh
set -euo pipefail
cd "$(dirname "$0")"
if [[ "${1:-}" == "--check" ]]; then
    ./test.sh
    uv build
    uvx twine check --strict dist/*.whl dist/*.tar.gz
    exit 0
fi
if [[ "${1:-}" == "--help" ]]; then
    echo "Usage: ./publish.sh [--check | --resume vX.Y.Z | patch | minor | major]"
    exit 0
fi
command -v gh >/dev/null
gh auth status
if [[ "${1:-}" == "--resume" ]]; then
    tag="${2:?Provide the existing release tag}"
else
    [[ "$(git branch --show-current)" == main ]] || { echo "Release from main" >&2; exit 1; }
    [[ -z "$(git status --porcelain)" ]] || { echo "Commit changes first" >&2; exit 1; }
    ./test.sh
    git fetch origin main --tags
    git merge-base --is-ancestor origin/main HEAD
    tag=$(uvx --from gitnextver==1.0.4 gitnextver --bump "${1:-patch}" --commit=False --pull=False)
fi
# Allow GitHub a short interval to register the tag event; never create a second tag on retry.
run_id=""
for _attempt in {1..12}; do
    run_id=$(gh run list --workflow release.yml --branch "$tag" --event push --json databaseId --jq '.[0].databaseId // empty')
    [[ -z "$run_id" ]] || break
    sleep 5
done
[[ -n "$run_id" ]] || { echo "No Release run found; retry ./publish.sh --resume $tag" >&2; exit 1; }
gh run watch "$run_id" --interval 20 --exit-status
artifacts="dist/$tag"
mkdir -p "$artifacts"
gh release download "$tag" --dir "$artifacts" --pattern '*.whl' --pattern '*.tar.gz' --clobber
uvx twine check --strict "$artifacts"/*
echo "Published $tag"
