#!/bin/bash

#!/bin/bash

### BEGIN INIT INFO
# Provides:             first_run
# Required-Start:       $remote_fs $syslog $ssh
# Required-Stop:        $remote_fs $syslog
# Default-Start:        5
# Default-Stop:         
# Short-Description:    Do a first run
### END INIT INFO

/first_run.sh | tee /first_run.log
/setup_k3s_worker.sh | tee /first_run.log
rm $0
