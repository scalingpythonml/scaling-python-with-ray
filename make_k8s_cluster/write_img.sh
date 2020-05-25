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
# Figure out how much free space we have and grow root to half of it + add a data dir
free_start=$(parted -m ${target} unit s print free | grep 'free;' | sort -t : -k 4n -k 2n | tail -n 1 | cut -f 2 -d ":" | cut -f 1 -d "s")
free_end=$(parted -m ${target} unit s print free | grep 'free;' | sort -t : -k 4n -k 2n | tail -n 1 | cut -f 3 -d ":" | cut -f 1 -d "s")
total=$(parted -m ${target} unit s print | grep ${target} | cut -f 2 -d ":" | cut -f 1 -d "s")
new_root_end=$(( ${free_start}+(${free_end}-${free_start})/2))
new_root_end_percent=$(( (100*${new_root_end})/${total} ))
data_start_loc=$(( (100*${new_root_end}+1)/${total}+1 ))
parted --align optimal ${target} resizepart ${root_partition} ${new_root_end_percent}%
sleep 1
partprobe ${target}
sleep 5
while [ ! -e ${target}${root_partition} ] || [ ! -b ${target}${root_partition} ]; do
  sleep 1
done
fsck -fy ${target}${root_partition}
resize2fs ${target}${root_partition}
fsck -fy ${target}${root_partition}
parted --align optimal ${target} mkpart primary ${data_start_loc}% '100%'
sync
sleep 1
eject ${target}
