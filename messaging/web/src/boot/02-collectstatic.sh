#!/bin/bash
set -e

if [ "$__ENV__" == "Test" ]; then
    echo "Collecting static files..."
    python manage.py collectstatic --dry-run --no-post-process --noinput
else
    python manage.py collectstatic --noinput
fi

exec "$@"
