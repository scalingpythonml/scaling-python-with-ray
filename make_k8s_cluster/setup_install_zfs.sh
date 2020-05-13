#!/bin/bash
set -ex
DEBIAN_FRONTEND=noninteractive
export DEBIAN_FRONTEND
# Flock so we don't step on the auto updaters toes
echo debconf zfs-dkms/note-incompatible-licenses select true | debconf-set-selections
echo debconf common/note-incompatible-licenses select true | debconf-set-selections
flock /var/lib/dpkg/lock -c "apt install -y zfs-dkms"
flock /var/lib/dpkg/lock -c "apt install -y zfsutils-linux"
# Discover all partitions for using, currently all non-mounted partitions
devices=$(lsblk -i |grep -v loop |grep -v / |grep part | grep -vi swap  | cut -d "-" -f 2 | cut -f 1 -d " ")
storage_devices=""
mkdir -p /storage_paths
for device in ${devices[@]}; do
  storage_devices="${storage_devices}/dev/${device} "
done
zpool create zfs-storage-pool ${storage_devices} -f
