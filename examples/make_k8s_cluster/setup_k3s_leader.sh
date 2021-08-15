#!/bin/bash
set -ex
# Clean up docker
docker system prune -af
docker network prune -f
K3S_NODE_NAME=$(hostname)
export K3S_NODE_NAME
leader_ip=$(nslookup k8s-leader.local | awk '/^Address: / { print $2 ; exit }')
curl -sfL https://get.k3s.io | INSTALL_K3S_VERSION=v1.18.8+k3s1 sh -s - --bind-address ${leader_ip} --node-ip ${leader_ip} --advertise-address ${leader_ip} --kubelet-arg="feature-gates=DevicePlugins=true"
