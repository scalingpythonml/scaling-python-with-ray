#!/bin/bash
set -ex

# Wait for the master to become discoverable
for i in {1..10}; do
  sleep ${i}
  ping -c 2 k8s-master.local && break || echo "Not yet"
done
# Add the masters ssh key automatically
mkdir -p ~/.ssh
ls ~/.ssh
ssh-keyscan k8s-master.local |& tee -a ~/.ssh/known_hosts
