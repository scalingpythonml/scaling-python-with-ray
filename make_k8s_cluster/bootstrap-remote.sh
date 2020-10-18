#!/bin/bash

set -ex

REMOTE_USER=${REMOTE_USER:-holden}
DEST="$REMOTE_USER@$TARGET_IP:"
COPY_COMMAND="scp"
RUN_DEST_CMD="ssh ${REMOTE_USER}@${TARGET_IP}"
TEE_DEST_CMD="ssh root@${TARGET_IP} tee -a "
DISABLE_CLOUD_CFG="true"
MAKE_DEST_DIR="ssh root@${TARGET_IP} mkdir -p "
K3S_SCRIPT=${K3S_SCRIPT:-"setup_k3s_worker_gpu"}

source bootstrap-funcs.sh

# Boot strap key based ssh access to user and root

# copy_ssh_keys_remote

DEST="root@$TARGET_IP:"
RUN_DEST_CMD="ssh root@${TARGET_IP}"

update_ubuntu
config_system

${COPY_COMMAND} firstboot.sh ${DEST}/etc/init.d/firstboot
${COPY_COMMAND} first_run_worker_remote.sh ${DEST}/do_firstboot.sh
${COPY_COMMAND} ${K3S_SCRIPT}.sh ${DEST}/setup_k3s_worker.sh
${RUN_DEST_CMD} chmod a+x /setup*.sh
${RUN_DEST_CMD} chmod a+x /etc/init.d/firstboot
${RUN_DEST_CMD} update-rc.d  firstboot defaults
# Don't do ZFS on these nodes by default
${RUN_DEST_CMD} echo "" > setup_install_zfs.sh
# ${RUN_DEST_CMD} reboot
