#!/bin/bash
set -ex
# Clean up docker
docker system prune -af
docker network prune
K3S_NODE_NAME=$(hostname)
export K3S_NODE_NAME
master_ip=$(nslookup k8s-master.local | awk '/^Address: / { print $2 ; exit }')
curl -sfL https://get.k3s.io | INSTALL_K3S_VERSION=v1.17.5+k3s1 sh -s - --bind-address ${master_ip} --node-ip ${master_ip} --advertise-address ${master_ip} --kubelet-arg="feature-gates=DevicePlugins=true"
