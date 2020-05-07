#!/bin/bash
set -ex
# Discover all XFS partitions for using, currently all non-mounted partitions
devices=$(lsblk -i |grep -v loop |grep -v / |grep part | grep -vi swap  | cut -d "-" -f 2 | cut -f 1 -d " ")
for device in ${devices[@]}; do
  mkdir -p /mnt/${device}
  fsck -t xfs /dev/${device} && echo "Adding ${device}" && echo "/dev/${device} /mnt/${device} xfs defaults 1 2" >> /etc/fstab
done
mount -a
# Get our ip address, check eth0 then wlan0
ip_addr=$(/sbin/ifconfig eth0 | grep 'inet addr:' | cut -d: -f2 | awk '{ print $1}'w)
if [ -z "$ip_addr" ]; then
  ip_addr=$(/sbin/ifconfig wlan0 | grep 'inet addr:' | cut -d: -f2 | awk '{ print $1}'w)
fi
# Add ourselves to the masters host file so we are discoverable
# For now we (hope) service disco does the trick
# ssh root@k8s-master.local -- echo "${ip_addr}     ${hostname} ${hostname}.local" >> /etc/hosts
# Trigger the bi-directional probe
gluster probe k8s-master.local &
ssh root@k8s-master.local gluster probe ${hostname}.local &
for device in ${devices[@]}; do
  if [ "$(ls -A /mnt/${device})" ]; then
    echo "${device} is not empty not adding to gluster."
  else
    mkdir /mnt/${device}/gv0
    gluster_paths="${gluster_paths}$(hostname).local:/mnt/${device}/gv0\n"
  fi
done
# Copy our gluster paths over
echo "${gluster_paths}" > /tmp/gluster_$(hostname)
scp /tmp/gluster_$(hostname) root@k8s-master.local:/gluster_paths/$(hostname)
