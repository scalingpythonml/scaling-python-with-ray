#!/bin/bash
DEBIAN_FRONTEND=noninteractive
export DEBIAN_FRONTEND
apt-get update
apt-get upgrade -y
# This makes debugging less work
apt-get install -y tmate emacs nano
# Necessary build magics
# Note: QEMU means we're running a different kernel
# than the one we use on the board
apt install -y linux-headers-raspi2  cmake gcc clang libyaml-cpp-dev libyaml-dev pkgconfig
# Install falco
git clone https://github.com/falcosecurity/falco.git
pushd falco
git pull
# This is from nova
git checkout origin/falco-on-arm
# Setup K3s


