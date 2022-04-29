#!/bin/bash
set -e

echo "Clearing stale cache..."
python manage.py clear_cache

exec "$@"
