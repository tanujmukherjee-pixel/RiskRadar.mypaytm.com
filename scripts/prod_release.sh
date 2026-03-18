#!/bin/bash

# exit when any command fails
set -euxo pipefail

release_version=$(python3 ./scripts/version.py get)
branch_name=${1:?branch name must be provided}
export ECR_REPO=${2:?AWS_ECR_REPO must be provided}
export PROFILE=${3:?profile must be provided}

# verify version incrementation is applied to permitted branch
if ! (echo "$branch_name" | grep -qe "^master$"); then
  printf '###\n### Production release script cannot be run on branch %s\n###\n' "$branch_name"
  exit 1
fi

# Tag release version in production branch
echo "Tagging production branch"
git config user.name "bitbucket-pipelines"
git config user.email ""
git tag  -a "$release_version" -m "Release version $release_version tag"
git push origin "${1}"
echo "Done tagging production branch"

timestamp=$(date +'%s')
short_commit_hash=$(git rev-parse --short HEAD)
development_version=${release_version}-${timestamp}-${short_commit_hash}

# Build & tag production and development images
export VERSION=${release_version}
export ADDITIONAL_VERSION=${development_version}
echo "Building and pushing image with production and development tag"
# Build and push docker image
make docker_build_for_deployment_multiple_tags
echo "Production tag built and pushed; Development tag built and pushed"

echo "Pipeline complete! Docker image tag is $release_version and $development_version"