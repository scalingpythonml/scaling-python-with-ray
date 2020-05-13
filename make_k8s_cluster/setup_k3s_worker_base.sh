#!/bin/bash
# Wait for avahi to discover the master
avahi-daemon  -r
for i in {1..10}; do
  sleep ${i}
  ping -c 2 k8s-master.local && break
done
WORKER_ID=$(ssh root@k8s-master.local /get_worker_id.sh)
echo "k8s-worker-${WORKER_ID}" > /etc/hostname
hostname $(cat /etc/hostname)
avahi-daemon  -r
sleep 5
avahi-daemon  -r
sleep 1
K3S_NODE_NAME=$(hostname)
export K3S_NODE_NAME
K3S_TOKEN=$(ssh root@k8s-master.local cat /var/lib/rancher/k3s/server/node-token)
my_ip=$(nslookup ${k3S_NODE_NAME}.local | awk '/^Address: / { print $2 ; exit }')
curl -sfL https://get.k3s.io | INSTALL_K3S_VERSION=v1.17.5+k3s1 K3S_URL=https://k8s-master.local:6443 K3S_TOKEN=${K3S_TOKEN} sh - --kubelet-arg="feature-gates=DevicePlugins=true" --node-ip ${my_ip}
