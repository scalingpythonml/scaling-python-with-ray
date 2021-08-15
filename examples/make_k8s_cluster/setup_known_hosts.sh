#!/bin/bash
set -ex

# Wait for the leader to become discoverable
for i in {1..10}; do
  sleep ${i}
  ping -c 2 k8s-leader.local && break || echo "Not yet"
done
# Add the leaders ssh key automatically
mkdir -p ~/.ssh
ls ~/.ssh
ssh-keyscan k8s-leader.local |& tee -a ~/.ssh/known_hosts
