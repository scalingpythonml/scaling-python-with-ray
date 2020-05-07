#!/bin/bash
set -ex
# In gigabytes. cloudinit cc_resizefs can control this
PI_TARGET_SIZE=${PI_TARGET_SIZE:-19}
#JETSON_DATA_SIZE
# Set up dependencies
command -v unxz || sudo apt-get install xz-utils
command -v kpartx || sudo apt install kpartx
command -v parted || sudo apt-get install parted
command -v axel || sudo apt-get install axel
# Setup qemu
command -v qemu-system-arm || sudo apt-get install qemu-system qemu-user-static qemu binfmt-support debootstrap
# Cleanup existing loopbacks
sudo losetup -D
# Download the base images
mkdir -p images
if [ ! -f images/jetson-nano.zip ] && [ ! -f images/sd-blob-b01.img ]; then
  axel https://developer.nvidia.com/jetson-nano-sd-card-image-r3231 -o images/jetson-nano.zip &
fi
if [ ! -f images/ubuntu-arm64.img.xz ] &&  [ ! -f images/ubuntu-arm64.img ]; then
  axel http://cdimage.ubuntu.com/releases/20.04/release/ubuntu-20.04-preinstalled-server-arm64+raspi.img.xz?_ga=2.44224356.1107789398.1588456160-1469204870.1587264737 -o images/ubuntu-arm64.img.xz
fi
if [ ! -f images/ubuntu-arm64.img ]; then
  pushd images; unxz images/ubuntu-arm64.img.xz; popd
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
}

cleanup_ubuntu_mounts () {
  paths=("ubuntu-image/proc" "ubuntu-image/dev/pts" "ubuntu-image/sys" "ubuntu-image/dev" "ubuntu-image")
  for unmount_please in ${paths[@]}; do
    for i in {1..5}; do
      sync && sudo umount $unmount_please && break || sleep 1;
    done
  done
}
copy_ssh_keys () {
  sudo mkdir -p ubuntu-image/root/.ssh
  sudo cp ~/.ssh/authorized_keys ubuntu-image/root/.ssh/
  cat ssh_secret.pub | sudo tee -a ubuntu-image/root/.ssh/authorized_keys
  GH_USER=${GH_USER:-holdenk}
  curl https://github.com/${GH_USER}.keys | sudo tee -a ubuntu-image/root/.ssh/authorized_keys
  sudo cp ssh_secret ubuntu-image/root/.ssh/id_rsa
  cat ~/.ssh/known_hosts | grep -v k8s-master | sudo tee ubuntu-image/root/.ssh/known_hosts
}
enable_chroot () {
  # Let us execute ARM binaries
  sudo cp /usr/bin/qemu-*-static ubuntu-image/usr/bin/
}
config_system () {
  # This _should_ let the wifi work if configured, but mixed success.
  if [ -f 50-cloud-init.yaml.custom ]; then
    sudo mkdir -p ubuntu-image/etc/netplan
    sudo cp 50-cloud-init.yaml.custom ubuntu-image/etc/netplan/50-cloud-init.yaml
    # Cloud config overwrites the network config on first boot if it's installed so
    # copy our network config into cloud config if it's present.
    # Also ask cloud config not to touch the network.
    if [ -d ubuntu-image/etc/cloud/cloud.cfg.d ]; then
      sudo cp 50-cloud-init.yaml.custom ubuntu-image/etc/cloud/cloud.cfg.d/custom-networking.cfg
      echo "network: {config: disabled}" | sudo tee -a  ubuntu-image/etc/cloud/cloud.cfg.d/99-disable-network-config.cfg
    fi
  fi
  if [ -f cloud.cfg.custom ]; then
    echo "Custom cloud cfg specified"
    if [ -f ubuntu-image/etc/cloud/cloud.cfg ]; then
      echo "Overwritting existing cloud config"
      sudo cp ubuntu-image/etc/cloud/cloud.cfg ubuntu-image/etc/cloud/cloud.cfg.back
      sudo cp cloud.cfg.custom ubuntu-image/etc/cloud/cloud.cfg
      sudo diff ubuntu-image/etc/cloud/cloud.cfg ubuntu-image/etc/cloud/cloud.cfg.back || true
    else
      echo "No existing cloud config, skipping."
    fi
  fi
  sudo cp setup_*.sh ubuntu-image/
  sudo cp first_run.sh ubuntu-image/
  sudo cp update_pi.sh ubuntu-image/
  # Technicall not mounts but being able to resolve is necessary for a lot
  sudo rm ubuntu-image/etc/resolv.conf
  sudo cp /etc/resolv.conf ubuntu-image/etc/resolv.conf
  sudo cp /etc/hosts ubuntu-image/etc/hosts
}
update_ubuntu () {
  enable_chroot
  config_system
  # Do whatever updates and setup we can now inside the chroot
  sudo chroot ubuntu-image/ /update_pi.sh
}
cleanup_misc () {
  sudo rm ubuntu-image/bin/qemu-*-static
}
resize_partition () {
  local img_name=$1
  local partition_num=$2
  local target_size=$3
  dd if=/dev/zero bs=1G count=$((${target_size} * 120/100)) of=./$img_name conv=sparse,notrunc oflag=append
  sudo parted ${img_name} resizepart ${partition_num} ${target_size}g
  sync
  sudo kpartx -d ${img_name}
  sudo kpartx -u ${img_name}
  partition=$(sudo kpartx -av ${img_name} | cut -f 3 -d " " | head -n ${partition_num} | tail -n 1)
  sudo e2fsck -f /dev/mapper/${partition}
  sudo resize2fs /dev/mapper/${partition}
  sync
  sudo e2fsck -f /dev/mapper/${partition}
  sleep 5
}
if [ ! -f images/ubuntu-arm64-customized.img ]; then
  cp images/ubuntu-arm64.img images/ubuntu-arm64-customized.img
  sudo kpartx -dv images/ubuntu-arm64-customized.img
  partition=$(sudo kpartx -av images/ubuntu-arm64-customized.img  | cut -f 3 -d " " | tail -n 1)
  sudo mount  /dev/mapper/${partition} ubuntu-image
  sync
  sleep 5
  # Extend the image
  sudo umount /dev/mapper/${partition}
  sync
  sleep 1
  sudo e2fsck -f /dev/mapper/${partition}
  sudo kpartx -dv images/ubuntu-arm64-customized.img
  sync
  sleep 5
  resize_partition images/ubuntu-arm64-customized.img 2 ${PI_TARGET_SIZE}
  setup_ubuntu_mounts
  copy_ssh_keys
  update_ubuntu
  cleanup_ubuntu_mounts
  sudo kpartx -dv images/ubuntu-arm64-customized.img
  sync
  sleep 5
fi
echo "Baking master/worker images"
# Setup K3s
if [ ! -f images/ubuntu-arm64-master.img ]; then
  # Setup the master
  cp images/ubuntu-arm64-customized.img images/ubuntu-arm64-master.img
  sudo kpartx -d images/ubuntu-arm64-master.img
  partition=$(sudo kpartx -uav images/ubuntu-arm64-master.img  | cut -f 3 -d " " | tail -n 1)
  setup_ubuntu_mounts
  sudo cp masterhost ubuntu-image/etc/hostname
  sudo cp first_run_master.sh ubuntu-image/etc/init.d/firstboot
  sudo chroot ubuntu-image/ update-rc.d  firstboot defaults
  cleanup_misc
  cleanup_ubuntu_mounts
  sudo kpartx -dv images/ubuntu-arm64-master.img
  # Setup the worker
  cp images/ubuntu-arm64-customized.img images/ubuntu-arm64-worker.img
  sudo kpartx -d images/ubuntu-arm64-worker.img
  partition=$(sudo kpartx -av images/ubuntu-arm64-worker.img  | cut -f 3 -d " " | tail -n 1)
  setup_ubuntu_mounts
  sudo cp first_run_worker.sh ubuntu-image/etc/init.d/firstboot
  sudo chroot ubuntu-image/ update-rc.d  firstboot defaults
  cleanup_misc
  cleanup_ubuntu_mounts
  sudo kpartx -dv images/ubuntu-arm64-worker.img
  sync
fi
echo "Baking jetson nano worker image"
if [ ! -f images/sd-blob-b01.img ]; then
  pushd images; unzip jetson-nano.zip; popd
fi
if [ ! -f images/jetson-nano-custom.img ]; then
  cp images/sd-blob-b01.img images/jetson-nano-custom.img
  sudo kpartx -d images/jetson-nano-custom.img
  partition=$(sudo kpartx -av images/jetson-nano-custom.img  | cut -f 3 -d " " | head -n 1)
  setup_ubuntu_mounts
  copy_ssh_keys
  # We'd need to grow the FS for this to succeed.
  # update_ubuntu
  # Instead we put that stuff in our first run steps
  enable_chroot
  config_system
  sudo cp update_pi.sh ubuntu-image/first_run.sh
  cat first_run.sh | sudo tee -a ubuntu-image/first_run.sh
  sudo cp first_run_worker.sh ubuntu-image/etc/init.d/firstboot
  sudo chroot ubuntu-image/ update-rc.d  firstboot defaults
  cleanup_misc
  cleanup_ubuntu_mounts
  # TODO: Add an ext4 partition with JETSON_DATA_SIZE
  sudo kpartx -dv images/jetson-nano-custom.img
fi
