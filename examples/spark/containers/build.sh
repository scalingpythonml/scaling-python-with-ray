#!/bin/bash
set -eux
#tag::dlspark[]
if [ ! -f spark-3.1.1-bin-hadoop3.2.tgz ]; then
  axel https://ftp.wayne.edu/apache/spark/spark-3.1.1/spark-3.1.1-bin-hadoop3.2.tgz
fi
rm -rf spark-3.1.1-bin-hadoop-3.2
if [ ! -d spark-3.1.1-bin-hadoop3.2 ]; then
  tar -xvf spark-3.1.1-bin-hadoop3.2.tgz
fi
# Set SPARK_HOME to extracted directory
SPARK_HOME=`pwd`/spark-3.1.1-bin-hadoop3.2
#end::dlspark[]
# Temporary
#if [ ! -d spark-3.1.2-SNAPSHOT-bin-3.2.0 ]; then
#  tar -xvf spark-3.1.2-SNAPSHOT-bin-3.2.0.tgz
#fi
#SPARK_HOME=`pwd`/spark-3.1.2-SNAPSHOT-bin-3.2.0
cp ./notebook/* ${SPARK_HOME}
cp ./python-executor/Dockerfile ${SPARK_HOME}/PyDockerfile
#tag::build_exec_containers[]
# Copy over python setup script so we can have matching pythons
SPARK_VERSION=3.1.1.11
cp pysetup.sh ${SPARK_HOME}/bin/
pushd ${SPARK_HOME}
SPARK_ROOT="$SPARK_HOME"
./bin/docker-image-tool.sh  -r holdenk -t v${SPARK_VERSION} -X -b java_image_tag=11-jre-slim -p PyDockerfile Dockerfile build
#end::build_exec_containers[]
#tag::build-notebook[]
docker buildx build -t holdenk/spark-notebook:v${SPARK_VERSION}  --platform linux/arm64,linux/amd64 --push .
#end::build-notebook[]
popd
