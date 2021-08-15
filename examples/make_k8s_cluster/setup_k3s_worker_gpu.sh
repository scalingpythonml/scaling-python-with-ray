#!/bin/bash
set -ex
# Clean up docker
docker system prune -af || echo "k"
docker network prune -f || echo "k"
INSTALL_K3S_EXEC="--docker"
export INSTALL_K3S_EXEC
K3S_EXTRA="--node-label role=gpu"
export K3S_EXTRA
source /setup_k3s_worker_base.sh
