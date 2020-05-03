#!/bin/bash
curl -sfL https://get.k3s.io | K3S_URL=https://k8s-master:6443 K3S_TOKEN=${K3S_TOKEN} sh -
