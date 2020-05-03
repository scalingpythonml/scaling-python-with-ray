#!/bin/bash
echo "k8s-worker-$(uuidgen)" > /etc/hostname
K3S_TOKEN=$(ssh root@k8s-master cat /var/lib/rancher/k3s/server/node-token)
curl -sfL https://get.k3s.io | K3S_URL=https://k8s-master:6443 K3S_TOKEN=${K3S_TOKEN} sh -

