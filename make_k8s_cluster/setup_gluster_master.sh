#!/bin/bash
set -ex
# Discover all XFS partitions for using, currently all non-mounted partitions
devices=$(lsblk -i |grep -v loop |grep -v / |grep part | grep -vi swap  | cut -d "-" -f 2 | cut -f 1 -d " ")
gluster_paths=""
for device in ${devices[@]}; do
  mkdir -p /mnt/${device}
  fsck -t xfs /dev/${device} && echo "Adding ${device}" && echo "/dev/${device} /mnt/${device} xfs defaults 1 2" >> /etc/fstab
done
mount -a
mkdir -p /gluster_paths
for device in ${devices[@]}; do
  if [ "$(ls -A /mnt/${device})" ]; then
    echo "${device} is not empty not adding to gluster."
  else
    mkdir /mnt/${device}/gv0
    gluster_paths="${gluster_paths}$(hostname).local:/mnt/device/gv0\n"
  fi
done
echo "${gluster_paths}" > /gluster_paths/$(hostname)
#Later, once the workers come up...
# gluster volume create gvol0 dispersed 3 $(cat /gluster_paths/*) force
