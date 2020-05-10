#!/bin/bash
set -ex
if [ ! -f /updated_pi ]; then
  DEBIAN_FRONTEND=noninteractive
  export DEBIAN_FRONTEND
  apt-get update
  apt-get upgrade -y
  # This makes debugging less work
  apt-get install -y emacs-nox nano
  apt-get install -y tmate net-tools nmap wireless-tools
  apt-get install -y ssh
  apt-get install -y jq
  # This helps us have working DNS magic
  apt-get install -y avahi-daemon libnss-mdns
  # Necessary build magics
  # Note: QEMU means we're running a different kernel
  # than the one we use on the board
  apt install -y linux-headers-raspi2 || echo "Probably not a pi image"
  apt install -y cmake gcc clang
  # Install some build libraries we need
  apt install -y libyaml-cpp-dev libyaml-dev pkg-config libjq-dev
  # For K3s
  apt install -y systemd-sysv
  # On the master we want to make our rook cluster after some time period
  apt-get install at
  # I hate netplan
  netplan generate
  # Start installing falco
  if [ ! -d falco ]; then
    git clone https://github.com/falcosecurity/falco.git
    pushd falco
    git pull
    # This is from nova
    git checkout origin/falco-on-arm
    popd
  fi
  touch /updated_pi
fi
