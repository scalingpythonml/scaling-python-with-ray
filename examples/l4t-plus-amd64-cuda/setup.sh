#!/bin/bash
set -ex
apt-get update -y
apt-get install -y wget
# tini isn't available in ubuntu 18.04 so manually dl and install
wget http://ftp.us.debian.org/debian/pool/main/t/tini/tini_0.18.0-1_${TARGETARCH}.deb
dpkg --install tini_0.18.0-1_${TARGETARCH}.deb
rm tini*.deb
