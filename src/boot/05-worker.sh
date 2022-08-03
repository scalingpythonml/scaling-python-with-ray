#!/bin/bash
set -e

if [ "$WEB_ONLY" != "TRUE" ]; then
  if [ "$__ENV__" != "Test" ]; then
    echo "Starting up queue workers..."
    supervisorctl -c /init/supervisord.conf start worker:*
    supervisorctl -c /init/supervisord.conf start transient_worker:*
  fi
fi

exec "$@"
