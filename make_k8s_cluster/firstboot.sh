#!/bin/bash

### BEGIN INIT INFO
# Provides:             firstboot
# Required-Start:       $remote_fs $syslog ssh networking
# Required-Stop:        $remote_fs $syslog
# Default-Start:        5
# Default-Stop:
# Short-Description:    Do a first run
### END INIT INFO
/do_firstboot.sh |& tee -a /firstboot.log &
disown $!
