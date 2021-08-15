#!/bin/bash
# Wait for avahi to discover the leader
set -x
avahi-daemon  -r
for i in {1..10}; do
  sleep ${i}
  ping -c 2 k8s-leader.local && break
done
WORKER_ID=${WORKER_ID:-$(ssh root@k8s-leader.local /get_worker_id.sh)}
K3S_EXTRA=${K3S_EXTRA:-"--node-label role=storage-node"}
echo "k8s-worker-${WORKER_ID}" > /etc/hostname
hostname $(cat /etc/hostname)
sync
sleep 1
# Reload is not enough :/
avahi-daemon -k || echo "avahi daemon not running"
sleep 5
avahi-daemon -D
sleep 1
# Wait for avahi to re-discover the leader
for i in {1..10}; do
  sleep ${i}
  ping -c 2 k8s-leader.local && break
done
K3S_NODE_NAME=$(hostname)
export K3S_NODE_NAME
K3S_TOKEN=$(ssh root@k8s-leader.local cat /var/lib/rancher/k3s/server/node-token)
my_ip=$(nslookup ${K3S_NODE_NAME}.local | awk '/^Address: / { print $2 ; exit }')
# k3s doesn't route it's disco through avahi, so we resolve the leader to /etc/hosts
# relatedly the leader IP needs to be pinned.
getent hosts k8s-leader.local >> /etc/hosts
curl -sfL https://get.k3s.io | INSTALL_K3S_VERSION=v1.18.8+k3s1 K3S_URL=https://k8s-leader.local:6443 K3S_TOKEN=${K3S_TOKEN} sh -s - --kubelet-arg="feature-gates=DevicePlugins=true" --node-ip ${my_ip} ${K3S_EXTRA}
