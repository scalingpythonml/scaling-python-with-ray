#!/bin/bash

REMOTE_USER=${REMOTE_USER:-holden}
DEST="$REMOTE_USER@$TARGET_IP:"
COPY_COMMAND="scp"
RUN_DEST_CMD="ssh ${REMOTE_USER}@${TARGET_IP}"
TEE_DEST_CMD="ssh root@${TARGET_IP} tee -a "
DISABLE_CLOUD_CFG="true"
MAKE_DEST_DIR="ssh root@${TARGET_IP} mkdir -p "

source bootstrap-funcs.sh

# Boot strap key based ssh access to user and root

# copy_ssh_keys_remote

DEST="root@$TARGET_IP:"
RUN_DEST_CMD="ssh root@${TARGET_IP}"

update_ubuntu
config_system
