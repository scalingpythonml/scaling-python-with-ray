#!/bin/bash
set -ex
# We install generic headers doing bootstrap, lets match our running kernel
DEBIAN_FRONTEND=noninteractive
export DEBIAN_FRONTEND
# Flock so we don't step on the auto updaters toes
flock /var/lib/dpkg/lock -c "apt-get update"
flock /var/lib/dpkg/lock -c "apt-get install -y linux-headers-$(uname -r)"
# We skip building falco for now because we're waiting on https://github.com/falcosecurity/falco/pull/1176
# /setup_falco.sh || echo "k"
