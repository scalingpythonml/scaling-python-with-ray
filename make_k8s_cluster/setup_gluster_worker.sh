#!/bin/bash
# Get our ip address, check eth0 then wlan0
ip_addr=$(/sbin/ifconfig eth0 | grep 'inet addr:' | cut -d: -f2 | awk '{ print $1}'w)
if [ -z "$ip_addr" ]; then
  ip_addr=$(/sbin/ifconfig wlan0 | grep 'inet addr:' | cut -d: -f2 | awk '{ print $1}'w)
fi
# Add ourselves to the masters host file so we are discoverable
ssh root@k8s-master.local -- echo "${ip_addr}     ${hostname}" >> /etc/hosts
# Trigger the bi-directional probe
gluster probe k8s-master.local &
ssh root@k8s-master.local gluster probe ${hostname} &
