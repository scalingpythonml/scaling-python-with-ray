#!/bin/bash
set -ex
# Install ZFS
./setup_install_zfs.sh
at now + 1 hour -f /setup_rook.sh
