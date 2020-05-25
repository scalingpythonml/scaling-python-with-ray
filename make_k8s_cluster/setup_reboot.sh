#!/bin/bash
# If we're blocked on shutdown needed...
echo "This seems silly, but we're going to give the system some time to apply any updates"
for i in {1..10}; do
  echo "Waiting ${i} before checking for reboot again"
  sleep ${i}
  cat /var/run/reboot-required && break || echo "Making sure we don't need to reboot..."
done
if [ -f /var/run/reboot-required ]; then
  echo "Seems like a reboot is required, restarting in 10."
  sleep 10
  shutdown -r now
fi
echo "No reboot, yay!"
exit 0
