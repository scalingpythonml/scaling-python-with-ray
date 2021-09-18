#!/bin/bash

#tag::deps[]
sudo apt-get install -y git tzdata bash libhdf5-dev curl pkg-config wget cmake build-essential \
  zlib1g-dev zlib1g openssh-client gnupg unzip libunwind8 libunwind-dev \
  openjdk-11-jdk git
# Depending on debain version
sudo apt-get install -y libhdf5-100 || sudo apt-get install -y libhdf5-103
# Install bazelisk to install bazel (needed for Ray's CPP code)
# See https://github.com/bazelbuild/bazelisk/releases
# On Linux ARM
BAZEL=bazelisk-linux-arm64
# On MAC ARM
# BAZEL=bazelisk-darwin-arm64
wget -q https://github.com/bazelbuild/bazelisk/releases/download/v1.10.1/${BAZEL} -O /tmp/bazel
chmod a+x /tmp/bazel
sudo mv /tmp/bazel /usr/bin/bazel
# Install node, needed for the UI
curl -fsSL https://deb.nodesource.com/setup_16.x | sudo bash -
sudo apt-get install -y nodejs
#end::deps[]
#tag::build[]
git clone https://github.com/ray-project/ray.git
cd ray
# Build the ray UI
pushd python/ray/new_dashboard/client; npm install && npm ci && npm run build; popd
# Specify a specific bazel version as newer ones sometimes break.
export USE_BAZEL_VERSION=3.7.2
# This part takes an hour on a modern ARM machine :(
./build.sh
cd python
# Install in edit mode or build a wheel
pip install -e .
# python setup.py bdist_wheel
#end::build[]
