#!/bin/bash
set -ex
# In gigabytes.
PI_TARGET_SIZE=${PI_TARGET_SIZE:-19}
JETSON_TARGET_SIZE=${JETSON_TARGET_SIZE:-24}
COPY_COMMAND=${COPY_COMMAND:-"sudo cp"}
DEST=${DEST:-ubuntu-image}
RUN_DEST_CMD=${RUN_DEST_CMD:-sudo chroot ubuntu-image/}
TEE_DEST_CMD=${TEE_DEST_CMD:-sudo tee -a ${DEST}}
MAKE_DEST_DIR=${MAKE_DEST_DIR:-sudo mkdir -p ${DEST}}
# Set up dependencies
command -v unxz || sudo apt-get install xz-utils
command -v kpartx || sudo apt install kpartx
command -v parted || sudo apt-get install parted
command -v axel || sudo apt-get install axel
command -v wget || sudo apt-get install wget
# Setup qemu
command -v qemu-system-arm || sudo apt-get install qemu-system qemu-user-static qemu binfmt-support debootstrap
# Download the base images
mkdir -p images
if [ ! -f images/jetson-nano.zip ] && [ ! -f images/sd-blob-b01.img ]; then
  # The redirects make axel not so happy here
  wget https://developer.nvidia.com/jetson-nano-sd-card-image -O images/jetson-nano.zip &
  jpid=$!
fi
if [ ! -f images/ubuntu-arm64.img.xz ] &&  [ ! -f images/ubuntu-arm64.img ]; then
  axel https://cdimage.ubuntu.com/releases/20.04.1/release/ubuntu-20.04.1-preinstalled-server-arm64+raspi.img.xz?_ga=2.269187633.1533046301.1598224230-102581225.1598224230 -o images/ubuntu-arm64.img.xz
fi
if [ ! -f images/ubuntu-arm64.img ]; then
  pushd images; unxz ubuntu-arm64.img.xz; popd
fi
# Download rook
if [ ! -d rook ]; then
  mkdir rook
  pushd rook
  git clone --single-branch --branch release-1.3 https://github.com/rook/rook.git
  popd
fi
# Make an ssh key for everyone to be able to talk to eachother
if [ ! -f ssh_secret ]; then
  ssh-keygen -f ssh_secret -N ""
fi

# Cleanup existing loopbacks
cleanup_ubuntu_mounts () {
  paths=("ubuntu-image/proc/sys/fs/binfmt_misc" "ubuntu-image/proc" "ubuntu-image/dev/pts" "ubuntu-image/sys" "ubuntu-image/dev" "ubuntu-image/boot" "ubuntu-image/boot/firmware" "ubuntu-image")
  for unmount_please in ${paths[@]}; do
    if [ -e ${unmount_please} ]; then
      mounted=$(mount |grep "${unmount_please} " || true)
      if [ ! -z "${mounted}" ]; then
	for i in {1..5}; do
	  if [ "{$i}" == "5" ]; then
	    sync && sudo umount $unmount_please && break || sudo umount -lf ${unmount_please};
	  else
	    sync && sudo umount $unmount_please && break || sleep ${i};
	  fi
	done
      fi
    fi
  done
}

prepare_local () {
  cleanup_ubuntu_mounts
  sleep 5 # losetup -D
  mkdir -p ubuntu-image
}

setup_ubuntu_mounts () {
  sudo mount  /dev/mapper/${partition} ubuntu-image
  sudo mount --bind /dev ubuntu-image/dev/
  sudo mount --bind /sys ubuntu-image/sys/
  sudo mount --bind /proc ubuntu-image/proc/
  sudo mount --bind /dev/pts ubuntu-image/dev/pts
  if [ ! -z "${boot_partition}" ]; then
    sudo mount /dev/mapper/${boot_partition} ubuntu-image/boot
  else
    echo "Skipping mounting boot partition"
  fi
  if [ ! -z "${firmware_boot_partition}" ]; then
    sudo mount /dev/mapper/${firmware_boot_partition} ubuntu-image/boot/firmware
  else
    echo "Skipping mounting boot firmware partition"
  fi
}
setup_jetson_img () {
  local img_name=$1
  sudo kpartx -d ${img_name}
  sudo kpartx -u ${img_name}
  partition=$(sudo kpartx -av ${img_name}  | cut -f 3 -d " " | head -n 1)
}
setup_ubuntu_server_img () {
  local img_name=$1
  sudo kpartx -d ${img_name}
  sudo kpartx -u ${img_name}
  firmware_boot_partition=$(sudo kpartx -av ${img_name} | cut -f 3 -d " " | head -n 1 | tail -n 1)
  partition=$(sudo kpartx -av ${img_name} | cut -f 3 -d " " | head -n 2 | tail -n 1)
}

# We normally are logging in as a special user
copy_ssh_keys_remote () {
  ${RUN_DEST_CMD} mkdir -p ~/.ssh
  ${COPY_COMMAND} ~/.ssh/authorized_keys ${DEST}~/.ssh/authorized_keys
  cat ssh_secret.pub | ${RUN_DEST_CMD} tee -a ~/.ssh/authorized_keys
  GH_USER=${GH_USER:-holdenk}
  curl https://github.com/${GH_USER}.keys | ${RUN_DEST_CMD} tee -a ~/authorized_keys
  ${COPY_COMMAND} ssh_secret ${DEST}~/.ssh/id_rsa
  ${RUN_DEST_CMD} "sudo -S sh -c \"mkdir -p /root/.ssh && cp -af ~${REMOTE_USER}/.ssh/* /root/.ssh/ && chown -R root /root/.ssh && chgrp -R root /root/.ssh\""
}

copy_ssh_keys () {
  ${MAKE_DEST_DIR}/root/.ssh
  ${COPY_COMMAND} ~/.ssh/authorized_keys ${DEST}/root/.ssh/
  cat ssh_secret.pub | ${TEE_DEST_CMD}/root/.ssh/authorized_keys
  GH_USER=${GH_USER:-holdenk}
  curl https://github.com/${GH_USER}.keys | ${TEE_DEST_CMD}/root/.ssh/authorized_keys
  ${COPY_COMMAND} ssh_secret ${DEST}/root/.ssh/id_rsa
}
setup_internet () {
  # Technicall not mounts but being able to resolve is necessary for a lot
  sudo rm ${DEST}/etc/resolv.conf
  ${COPY_COMMAND} /etc/resolv.conf ${DEST}/etc/resolv.conf
  ${COPY_COMMAND} /etc/hosts ${DEST}/etc/hosts
}

enable_chroot () {
  # Let us execute ARM binaries
  setup_internet
  ${COPY_COMMAND} /usr/bin/qemu-*-static ${DEST}/usr/bin/
}
config_system () {
  # Configure avahi to only be active on select interfaces
  ${COPY_COMMAND} avahi-daemon.conf ${DEST}/etc/avahi/avahi-daemon.conf
  # Copy any extra env settings
  if [ -f myenv.custom ]; then
    cat myenv.custom | ${TEE_DEST_CMD}/etc/environment
  fi
  # On the remote systems cloud cfg will have already run
  if [ -z "${DISABLE_CLOUD_CFG}" ]; then
    # This _should_ let the wifi work if configured, but mixed success.
    if [ -f 50-cloud-init.yaml.custom ]; then
      ${MAKE_DEST_DIR}/etc/netplan
      ${COPY_COMMAND} 50-cloud-init.yaml.custom ${DEST}/etc/netplan/50-cloud-init.yaml
      # Cloud config overwrites the network config on first boot if it's installed so
      # copy our network config into cloud config if it's present.
      # Also ask cloud config not to touch the network.
      if [ -d ${DEST}/etc/cloud/cloud.cfg.d ]; then
	${COPY_COMMAND} 50-cloud-init.yaml.custom ${DEST}/etc/cloud/cloud.cfg.d/custom-networking.cfg
	echo "network: {config: disabled}" | sudo tee -a  ${DEST}/etc/cloud/cloud.cfg.d/99-disable-network-config.cfg
      fi
    fi
    if [ -f cloud.cfg.custom ]; then
      echo "Custom cloud cfg specified"
      if [ -f ${DEST}/etc/cloud/cloud.cfg ]; then
	echo "Overwritting existing cloud config"
	${COPY_COMMAND} ${DEST}/etc/cloud/cloud.cfg ${DEST}/etc/cloud/cloud.cfg.back
	${COPY_COMMAND} cloud.cfg.custom ${DEST}/etc/cloud/cloud.cfg
	sudo diff ${DEST}/etc/cloud/cloud.cfg ${DEST}/etc/cloud/cloud.cfg.back || true
      else
	echo "No existing cloud config, skipping."
      fi
    fi
  fi
  ${COPY_COMMAND} setup_*.sh ${DEST}/
  ${COPY_COMMAND} wait_for*.sh ${DEST}/
  ${COPY_COMMAND} get_worker_id.sh ${DEST}/
  ${COPY_COMMAND} first_run.sh ${DEST}/
  ${COPY_COMMAND} update_pi.sh ${DEST}/
  # On the rasberry pi enable cgroup memory
  if [ -d ${DEST}/boot/firmware ]; then
    echo "cgroup_memory=1 cgroup_enable=memory cgroup_enable=cpuset $(cat ${DEST}/boot/firmware/cmdline.txt || true)" | sudo tee ${DEST}/boot/firmware/cmdline.txt
  fi
}
update_ubuntu () {
  # Do whatever updates and setup we can now inside the chroot
  ${COPY_COMMAND} update_pi.sh ${DEST}/
  ${RUN_DEST_CMD} /update_pi.sh
}
cleanup_misc () {
  sudo rm ${DEST}/bin/qemu-*-static
}
resize_partition () {
  local img_name=$1
  local partition_num=$2
  local target_size=$3
  dd if=/dev/zero bs=1G count=$((${target_size} * 120/100)) of=./$img_name conv=sparse,notrunc oflag=append
  sync
  sleep 1
  partprobe ${img_name}
  sleep 1
  # If we're in gpt land resize
  part_info=$(fdisk -l ${img_name} |grep "type: gpt" || true)
  if [ ! -z "${part_info}" ]; then
    sgdisk ${img_name} -e
  fi
  sleep 5
  sudo parted --script ${img_name} resizepart ${partition_num} ${target_size}g
  sync
  partprobe ${img_name}
  sleep 5
  sudo kpartx -d ${img_name}
  sudo kpartx -u ${img_name}
  partition=$(sudo kpartx -av ${img_name} | cut -f 3 -d " " | head -n ${partition_num} | tail -n 1)
  sudo e2fsck -f /dev/mapper/${partition}
  sudo resize2fs /dev/mapper/${partition}
  sync
  sudo e2fsck -f /dev/mapper/${partition}
  sleep 5
}
