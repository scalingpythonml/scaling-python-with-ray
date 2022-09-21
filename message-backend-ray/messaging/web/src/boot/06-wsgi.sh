#!/bin/bash
set -e

if [ "$__ENV__" != "Test" ]; then
    echo "Starting up wsgi server..."
    supervisorctl -c /init/supervisord.conf start wsgi:*
fi

exec "$@"
