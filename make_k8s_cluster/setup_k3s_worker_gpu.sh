#!/bin/bash
set -ex
# Clean up docker
docker system prune -af || echo "k"
docker network prune || echo "k"
INSTALL_K3S_EXEC="--docker"
export INSTALL_K3S_EXEC
source setup_k3s_worker_base.sh
