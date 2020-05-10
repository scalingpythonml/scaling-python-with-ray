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
K3S_TOKEN=$(ssh root@k8s-master.local cat /var/lib/rancher/k3s/server/node-token)
curl -sfL https://get.k3s.io | K3S_URL=https://k8s-master.local:6443 K3S_TOKEN=${K3S_TOKEN} sh -
