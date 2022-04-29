#!/bin/bash
set -e

if [ "$__ENV__" != "Test" ]; then
    echo "Starting up beat instance..."
    supervisorctl -c /init/supervisord.conf start beat
fi

exec "$@"
