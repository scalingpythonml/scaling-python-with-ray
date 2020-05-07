#!/bin/bash
set -ex
# Discover all partitions for using, currently all non-mounted partitions
devices=$(lsblk -i |grep -v loop |grep -v / |grep part | grep -vi swap  | cut -d "-" -f 2 | cut -f 1 -d " ")
storage_paths=""
for device in ${devices[@]}; do
  storage_paths="${storage_paths}$(hostname):${device}\n"
done
# Copy our paths over
echo "${storage_paths}" > /tmp/storage_$(hostname)
scp /tmp/storage_$(hostname) root@k8s-master.local:/storage_paths/$(hostname)
