#!/bin/bash
set -ex
# We install generic headers doing bootstrap, lets match our running kernel
DEBIAN_FRONTEND=noninteractive
export DEBIAN_FRONTEND
sudo apt-get install linux-headers-`uname -r`
# Ok now we _should_ be able to build falco
/setup_falco.sh || echo "k"
