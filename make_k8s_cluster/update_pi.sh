#!/bin/bash
set -ex
DEBIAN_FRONTEND=noninteractive
export DEBIAN_FRONTEND
apt-get update
apt-get upgrade -y
# This makes debugging less work
apt-get install -y tmate emacs nano
# Necessary build magics
# Note: QEMU means we're running a different kernel
# than the one we use on the board
apt install -y linux-headers-raspi2  cmake gcc clang libyaml-cpp-dev libyaml-dev pkg-config curl
# Start installing falco
if [ ! -d falco ]; then
  git clone https://github.com/falcosecurity/falco.git
  pushd falco
  git pull
  # This is from nova
  git checkout origin/falco-on-arm
  popd
fi
