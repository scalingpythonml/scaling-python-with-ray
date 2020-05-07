#!/bin/bash
set -ex
# Discover all partitions for using, currently all non-mounted partitions
devices=$(lsblk -i |grep -v loop |grep -v / |grep part | grep -vi swap  | cut -d "-" -f 2 | cut -f 1 -d " ")
storage_paths=""
mkdir -p /storage_paths
for device in ${devices[@]}; do
  storage_paths="${storage_paths}$(hostname):${device}\n"
done
echo "${gluster_paths}" > /storage_paths/$(hostname)
#Later, once the workers come up...
