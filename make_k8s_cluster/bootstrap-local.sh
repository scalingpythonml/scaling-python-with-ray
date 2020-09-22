#!/bin/bash

source bootstrap-funcs.sh

prepare_local

cleanup_ubuntu_mounts
if [ ! -f images/ubuntu-arm64-customized.img ]; then
  cp images/ubuntu-arm64.img images/ubuntu-arm64-customized.img
  setup_ubuntu_server_img images/ubuntu-arm64-customized.img
  # Extend the image, first check the current FS
  sudo umount /dev/mapper/${partition} || echo "not mounted :)"
  sync
  sleep 1
  sudo e2fsck -f /dev/mapper/${partition}
  sudo kpartx -dv images/ubuntu-arm64-customized.img
  sync
  sleep 5
  resize_partition images/ubuntu-arm64-customized.img 2 ${PI_TARGET_SIZE}
  setup_ubuntu_server_img images/ubuntu-arm64-customized.img
  setup_ubuntu_mounts
  enable_chroot
  update_ubuntu
  cleanup_ubuntu_mounts
  sudo kpartx -dv images/ubuntu-arm64-customized.img
  sync
  sleep 5
fi
echo "Baking leader/worker images"
# Setup K3s
if [ ! -f images/ubuntu-arm64-leader.img ]; then
  # Setup the leader
  cp images/ubuntu-arm64-customized.img images/ubuntu-arm64-leader.img
  setup_ubuntu_server_img images/ubuntu-arm64-leader.img
  setup_ubuntu_mounts
  copy_ssh_keys
  config_system
  ${COPY_COMMAND} leaderhost ubuntu-image/etc/hostname
  ${COPY_COMMAND} firstboot.sh ubuntu-image/etc/init.d/firstboot
  ${COPY_COMMAND} first_run_leader.sh ubuntu-image/do_firstboot.sh
  ${RUN_DEST_CMD} update-rc.d  firstboot defaults
  # The leader needs to have rook checked out
  ${COPY_COMMAND} -af rook ubuntu-image/
  ${COPY_COMMAND} setup_*.sh ubuntu-image/
  # Note operator.yaml change v2.1.1 to v2.1.1-arm64
  ${COPY_COMMAND} rook_*.yaml ubuntu-image/rook/cluster/examples/kubernetes/ceph/
  # The leader has a worker counter file
  ${COPY_COMMAND} worker_counter.txt ubuntu-image/
  cleanup_misc
  cleanup_ubuntu_mounts
  sudo kpartx -dv images/ubuntu-arm64-leader.img
  # Setup the worker
  cp images/ubuntu-arm64-customized.img images/ubuntu-arm64-worker.img
  setup_ubuntu_server_img images/ubuntu-arm64-worker.img
  setup_ubuntu_mounts
  copy_ssh_keys
  config_system
  ${COPY_COMMAND} firstboot.sh ubuntu-image/etc/init.d/firstboot
  ${COPY_COMMAND} first_run_worker.sh ubuntu-image/do_firstboot.sh
  ${RUN_DEST_CMD} update-rc.d  firstboot defaults
  cleanup_misc
  cleanup_ubuntu_mounts
  sudo kpartx -dv images/ubuntu-arm64-worker.img
  sync
fi
