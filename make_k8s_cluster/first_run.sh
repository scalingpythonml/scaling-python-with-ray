#!/bin/bash
set -ex
DEBIAN_FRONTEND=noninteractive
export DEBIAN_FRONTEND
sudo apt-get --reinstall install linux-headers-`uname -r`
/setup_falco.sh
