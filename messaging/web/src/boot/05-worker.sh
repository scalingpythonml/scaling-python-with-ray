#!/bin/bash
set -e

if [ "$__ENV__" != "Test" ]; then
    echo "Starting up queue workers..."
    supervisorctl -c /init/supervisord.conf start worker:*
    supervisorctl -c /init/supervisord.conf start transient_worker:*
fi

exec "$@"
