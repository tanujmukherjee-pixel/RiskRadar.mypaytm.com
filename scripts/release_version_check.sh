#!/bin/bash

# exit when any command fails
set -euxo pipefail

VERSION=$(python3 ./scripts/version.py get)

if git ls-remote --exit-code origin refs/tags/"$VERSION"; then
  printf '###\n### Release version tag %s already exist in the repository. Increment version before complete the release!\n###\n' "$VERSION"
  exit 1
else
  printf '###\n### Release version %s available for tagging. Ok to proceed.\n###\n' "$VERSION"
fi
