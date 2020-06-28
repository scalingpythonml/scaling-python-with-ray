#!/bin/bash

### BEGIN INIT INFO
# Provides:             first_run
# Required-Start:       $remote_fs $syslog ssh networking
# Required-Stop:
# Default-Start:        5
# Default-Stop:
# Short-Description:    Do a first run
### END INIT INFO

set +e
set -x
if [ ! -f /first_run_done ]; then
  echo "Doing first run as $(whoami)" |& tee -a /first_run.log
  echo "Starting first_run with a good 15 minute nap" |& tee -a  /first_run.log
  (sleep 900 || echo "Sleep failed?") |& tee -a /first_run.log
  echo "Done sleeping" |& tee -a  /first_run.log
  /wait_for_cloud_init.sh |& tee -a /first_run.log
  /setup_reboot.sh |& tee -a /first_run.log
  /first_run.sh |& tee -a  /first_run.log
  /setup_k3s_leader.sh |& tee -a  /first_run.log
  /setup_storage_leader.sh |& tee -a  /first_run.log
  touch /first_run_done
fi
