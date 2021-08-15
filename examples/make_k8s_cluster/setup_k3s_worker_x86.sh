#!/bin/bash
set -ex
# Clean up docker
docker system prune -af || echo "k"
docker network prune -f || echo "k"
K3S_EXTRA="--node-label role=x86"
export K3S_EXTRA
source /setup_k3s_worker_base.sh
