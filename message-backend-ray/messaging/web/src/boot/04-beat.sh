#!/bin/bash
set -e

if [ "$WEB_ONLY" != "TRUE" ]; then
  if [ "$__ENV__" != "Test" ]; then
    echo "Starting up beat instance..."
    supervisorctl -c /init/supervisord.conf start beat
  fi
fi

exec "$@"
