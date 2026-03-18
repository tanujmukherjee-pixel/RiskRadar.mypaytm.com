#!/bin/bash

# exit when any command fails
set -euxo pipefail

BRANCH=${1}
RELEASE_TYPE=${2}

# verify version incrementation is applied to permitted branch
if ! (echo "$BRANCH" | grep -qe "^develop"); then
  printf '###\n### Version number change is not allowed in branch %s\n###\n' "$BRANCH"
  exit 1
fi

# increment version number
LAST_VERSION=$(python3 ./scripts/version.py get)
printf '###\n### Version before incrementation is %s\n' "$LAST_VERSION"
echo "### $RELEASE_TYPE version will be incremented"
python3 ./scripts/version.py inc-"$RELEASE_TYPE"
VERSION=$(python3 ./scripts/version.py get)
printf '### Version after incrementation is %s###\n###\n' "$VERSION"

# Commit version number change
git config user.name "bitbucket-pipelines"
git config user.email ""
git add "VERSION"
git commit -m "Incrementing working version from $LAST_VERSION to $VERSION for production release."
git push origin "$BRANCH"