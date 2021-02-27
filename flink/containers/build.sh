#!/bin/bash
set -eux
#tag::dlflink[]
if [ ! -d flink-docker ]; then
  git@github.com:apache/flink-docker.git
fi
#end::dlflink[]
#tag::build[]
pushd flink-docker/1.12/scala_2.12-java11-debian
docker buildx build -t holdenk/flink:1.12 .  --platform linux/arm64,linux/amd64 --push
popd
docker buildx build -t holdenk/pyflink:1.12 . --build-arg base_img=holdenk/flink:1.12 --platform linux/arm64,linux/amd64 -f python-executor/Dockerfile --push
docker buildx build  -t holdenk/flink-notebook:1.12 . --platform linux/arm64,linux/amd64 -f notebook/Dockerfile --push
#end::build[]
