#!/bin/bash

set -xe

export GIT_COMMIT_HASH=$(git rev-parse HEAD)
echo "Building commit hash: $GIT_COMMIT_HASH into frontend container image"

docker build --tag node-explorer-frontend --build-arg GIT_COMMIT_HASH explorer-frontend/
docker build --tag node-explorer explorer-backend/