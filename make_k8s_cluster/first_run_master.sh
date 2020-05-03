#!/bin/bash

### BEGIN INIT INFO
# Provides:             first_run
# Required-Start:       $remote_fs $syslog ssh networking
# Required-Stop:
# Default-Start:        5
# Default-Stop:         
# Short-Description:    Do a first run
### END INIT INFO

if [ ! -f /first_run_done ]; then
  /first_run.sh | tee /first_run.log
  /setup_k3s_master.sh | tee /first_run.log
  touch /first_run_done
fi

