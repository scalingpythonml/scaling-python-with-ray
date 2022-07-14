#!/bin/bash
set -e

if [ "$__ENV__" != "Test" ]; then
    echo "Syncing databases..."
    python manage.py migrate --noinput --database default
fi

exec "$@"
