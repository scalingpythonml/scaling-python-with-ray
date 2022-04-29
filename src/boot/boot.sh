#!/bin/bash
set -e

if [ "$__ENV__" != "Local" ]; then
    run-parts --report --verbose --exit-on-error --regex "^[0-9]+\-[0-9a-z-]+\.sh$" "$(dirname "$0")"
fi

exec "$@"
