#!/bin/bash
set -eux
#tag::dlflink[]
if [ ! -d flink-docker ]; then
  git@github.com:apache/flink-docker.git
fi
#end::dlflink[]
#tag::build[]
cd flink-docker
cd 1.12
cd scala_2.12-java11-debian
docker buildx build -t holdenk/flink:1.12 .  --platform linux/arm64,linux/amd64 --push
#end::build[]
