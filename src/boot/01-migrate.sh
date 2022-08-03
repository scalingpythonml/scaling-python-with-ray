#!/bin/bash
set -e

if [ "$WEB_ONLY" != "TRUE" ]; then
  if [ "$__ENV__" != "Test" ]; then
    echo "Syncing databases..."
    python manage.py migrate --noinput --database default
  fi
fi

exec "$@"
