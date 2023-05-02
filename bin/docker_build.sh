#!/bin/bash

set -xe

docker build --tag node-explorer-frontend explorer-frontend/
docker build --tag node-explorer explorer-backend/