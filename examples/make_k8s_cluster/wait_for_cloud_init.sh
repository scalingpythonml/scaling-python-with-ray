#!/bin/bash
set -ex

if [ -d /var/lib/cloud ]; then
  echo "/var/lib/cloud exists, waiting for finish file to exist."
  for i in {1..100}; do
    echo "Waiting ${i} before checking again"
    sleep ${i}
    cat /var/lib/cloud/instance/boot-finished && break || echo "Waiting for cloud init to write boot-finished"
  done
else
  echo "No /var/lib/cloud, party"
fi

# Wait for apt daily upgrades
systemd-run --property="After=apt-daily.service apt-daily-upgrade.service" --wait /bin/true || echo "No waiting, yay!"
