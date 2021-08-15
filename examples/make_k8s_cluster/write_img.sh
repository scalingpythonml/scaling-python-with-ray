#!/bin/bash
set -ex
if [ -z "$1" ] || [ -z "$2" ] || [ ! -f "$1" ]; then
  echo "Usage: write_img [img] [device]"
  exit 1
fi
img=$1
target=$2
root_partition=${root_partition:-2}
umount ${target}* || echo "Didn't need to umount target"
# Wipe the disk
wipefs $2${root_partition} || echo "No need to wipefs"
dd if=${img} of=${target} bs=1M  # conv=sparse
sync
sleep 1
# Rescan the disk
partprobe ${target}
sleep 1
# If we're in gpt land resize
part_info=$(fdisk -l ${target} |grep -i "type: gpt" || true)
if [ ! -z "${part_info}" ]; then
  sgdisk ${target} -e
fi
partprobe ${target}
sleep 1
umount ${target}* || echo "Didn't need to umount target"
# Wait for the partitions to exist again
while [ ! -e ${target}${root_partition} ] || [ ! -b ${target}${root_partition} ]; do
  sleep 1
done
fsck -fy ${target}${root_partition}
parted --align optimal ${target} resizepart ${root_partition} '100%'
sleep 1
partprobe ${target}
sleep 5
while [ ! -e ${target}${root_partition} ] || [ ! -b ${target}${root_partition} ]; do
  sleep 1
done
fsck -fy ${target}${root_partition}
resize2fs ${target}${root_partition}
fsck -fy ${target}${root_partition}
sync
sleep 1
eject ${target}
