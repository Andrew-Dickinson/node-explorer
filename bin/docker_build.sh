#!/bin/bash

set -xe

export GIT_COMMIT_HASH=$(git rev-parse HEAD)
echo "Building commit hash: $GIT_COMMIT_HASH into frontend container image"

docker build --tag node-explorer-frontend explorer-frontend/
docker build --tag node-explorer explorer-backend/