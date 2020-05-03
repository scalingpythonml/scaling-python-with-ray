#!/bin/bash
set -ex
# In gigabytes
PI_TARGET_SIZE=${PI_TARGET_SIZE:-21}
JETSON_TARGET_SIZE=${JETSON_TARGET_SIZE:-110}
# Set up dependencies
command -v unxz || sudo apt-get install xz-utils
command -v kpartx || sudo apt install kpartx
command -v parted || sudo apt-get install parted
# Setup qemu
command -v qemu-system-arm || sudo apt-get install qemu-system qemu-user-static
# Cleanup existing loopbacks
sudo losetup -D
# Download the base images
if [ ! -f ubuntu-arm64.img.xz ] &&  [ ! -f ubuntu-arm64.img ]; then
  wget http://cdimage.ubuntu.com/releases/20.04/release/ubuntu-20.04-preinstalled-server-arm64+raspi.img.xz?_ga=2.44224356.1107789398.1588456160-1469204870.1587264737 -O ubuntu-arm64.img.xz
fi
if [ ! -f ubuntu-arm64.img ]; then
  unxz ubuntu-arm64.img.xz
fi
# Make an ssh key for everyone to be able to talk to eachother
if [ ! -f ssh_secret ]; then
  ssh-keygen -f ssh_secret -N ""
fi
mkdir -p ubuntu-image
setup_ubuntu_mounts () {
  sudo mount  /dev/mapper/${partition} ubuntu-image
  sudo mount --bind /dev ubuntu-image/dev/
  sudo mount --bind /sys ubuntu-image/sys/
  sudo mount --bind /proc ubuntu-image/proc/
  sudo mount --bind /dev/pts ubuntu-image/dev/pts
  sudo rm ubuntu-image/etc/resolv.conf
  sudo cp /etc/resolv.conf ubuntu-image/etc/resolv.conf
}
cleanup_ubuntu_mounts () {
  sync
  sleep 1
  sudo umount ubuntu-image/proc ubuntu-image/dev/pts || (sleep 1 && sudo umount ubuntu-image/proc ubuntu-image/dev/pts)
  sync
  sudo umount ubuntu-image/sys ubuntu-image/dev || (sleep 1 && sudo umount ubuntu-image/sys ubuntu-image/dev)
  sync
  sudo umount ubuntu-image || (sleep 1 && sudo umount ubuntu-image)
  sync
}
copy_ssh_keys () {
  sudo mkdir -p ubuntu-image/root/.ssh
  sudo cp ~/.ssh/authorized_keys ubuntu-image/root/.ssh/
  cat ssh_secret.pub | sudo tee ubuntu-image/root/.ssh/authorized_keys
  GH_USER=${GH_USER:-holdenk}
  curl https://github.com/${GH_USER}.keys | sudo tee ubuntu-image/root/.ssh/authorized_keys
  sudo cp secret ubuntu-image/root/.ssh/id_rsa
  sudo cp ~/.ssh/known_hosts ubuntu-image/root/.ssh/
}
update_ubuntu () {
  sudo cp /usr/bin/qemu-arm-static ubuntu-image/usr/bin/
  sudo cp update_pi.sh ubuntu-image/
  sudo chroot ubuntu-image/ /update_pi.sh
  # I'm not super sure bout this
  sudo cp 50-cloud-init.yaml.custom ubuntu-image/etc/netplan/50-cloud-init.yaml || echo "No custom network"
  sudo cp setup_*.sh ubuntu-image/
  sudo cp first_run.sh ubuntu-image/
}
function resize_partition {
  dd if=/dev/zero bs=1G count=$((${TARGET_SIZE}+2)) of=./ubuntu-arm64-customized.img conv=sparse,notrunc oflag=append
  sudo parted ubuntu-arm64-customized.img resizepart 2 ${TARGET_SIZE}g
  partition=$(sudo kpartx -av ubuntu-arm64-customized.img  | cut -f 3 -d " " | tail -n 1)
  sudo e2fsck -f /dev/mapper/${partition}
  sudo resize2fs /dev/mapper/${partition}
  sync
  sleep 5
}
if [ ! -f ubuntu-arm64-customized.img ]; then
  cp ubuntu-arm64.img ubuntu-arm64-customized.img
  partition=$(sudo kpartx -av ubuntu-arm64-customized.img  | cut -f 3 -d " " | tail -n 1)
  sudo mount  /dev/mapper/${partition} ubuntu-image
  sync
  sleep 5
  # Extend the image
  sudo umount /dev/mapper/${partition}
  sync
  sleep 1
  sudo e2fsck -f /dev/mapper/${partition}
  sudo kpartx -dv ubuntu-arm64-customized.img
  sync
  sleep 5
  TARGET_SIZE=${PI_TARGET_SIZE}
  resize_partition
  setup_ubuntu_mounts
  update_ubuntu
  cleanup_ubuntu_mounts
  sudo kpartx -dv ubuntu-arm64-customized.img
fi
echo "Baking master/worker images"
# Setup K3s
if [ ! -f ubuntu-arm64-master.img ]; then
  # Setup the master
  cp ubuntu-arm64-customized.img ubuntu-arm64-master.img
  partition=$(sudo kpartx -av ubuntu-arm64-master.img  | cut -f 3 -d " " | tail -n 1)
  setup_ubuntu_mounts
  sudo chroot ubuntu-image/ /usr/bin/hostname k8s-master
  sudo cp first_run_master.sh ubuntu-image/etc/rc5.d/S99-firstboot.sh
  cleanup_ubuntu_mounts
  sudo kpartx -dv ubuntu-arm64-master.img
  # Setup the worker
  cp ubuntu-arm64-customized.img ubuntu-arm64-worker.img
  partition=$(sudo kpartx -av ubuntu-arm64-worker.img  | cut -f 3 -d " " | tail -n 1)
  setup_ubuntu_mounts
  sudo cp first_run_worker.sh ubuntu-image/etc/rc5.d/S99-firstboot.sh
  cleanup_ubuntu_mounts
  sudo kpartx -dv ubuntu-arm64-worker.img
  sync
fi
echo "Baking jetson nano worker image"
if [ ! -f jetson-nano.zip ] && [ ! -f sd-blob-b01.img ]; then
  wget https://developer.nvidia.com/jetson-nano-sd-card-image -O jetson-nano.zip
fi
if [ ! -f sd-blob-b01.img ]; then
  unzip jetson-nano.zip
fi
if [ ! -f jetson-nano-custom.img ]; then
  cp sd-blob-b01.img jetson-nano-custom.img
  partition=$(sudo kpartx -av jetson-nano-custom.img  | cut -f 3 -d " " | head -n 1)
  setup_ubuntu_mounts
  copy_ssh_keys
  cleanup_ubuntu_mounts
  TARGET_SIZE=${JETSON_TARGET_SIZE}
  resize_partition
  setup_ubuntu_mounts
  update_ubuntu
  sudo cp first_run_worker.sh ubuntu-image/etc/rc5.d/S99-firstboot.sh
  cleanup_ubuntu_mounts
  sudo kpartx -dv jetson-nano-custom.img
fi
