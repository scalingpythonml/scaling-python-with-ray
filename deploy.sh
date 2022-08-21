#!/bin/bash

set -ex

docker buildx build . --platform=linux/arm64,linux/amd64 -t holdenk/messaging-backend:0.1a --push

ray exec --start --screen raycluster.yaml  "cd /apps/; python ./messaging/main.py"
