#!/bin/bash

# exit when any command fails
set -euxo pipefail

release_version=$(python3 ./scripts/version.py get)
timestamp=$(date +'%s')
short_commit_hash=$(git rev-parse --short HEAD)
# replace '/' in branch name with '-' to comply with docker tag naming rules
branch_name=$(echo "${1:?BITBUCKET_BRANCH must be provided}" | tr '/' '-')

export VERSION=${release_version}-${branch_name}-${timestamp}-${short_commit_hash}
export ECR_REPO=${2:?AWS_ECR_REPO must be provided}
export PROFILE=${3:-default}

# Build and push docker image
make docker_build_for_deployment

echo $VERSION > VERSION

# Commit version number change
git config user.name "bitbucket-pipelines"
git config user.email ""
git add "VERSION"
git commit -m "Updating working version to $VERSION for dev release."
git push origin "${1}"

echo "Pipeline complete! Docker image tag is $VERSION"
