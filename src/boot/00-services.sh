#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

function file_env(){
	local var="$1"
	local fileVar="${var}_FILE"
	local def="${2:-}"
	if [ "${!var:-}" ] && [ "${!fileVar:-}" ]; then
		echo >&2 "error: both $var and $fileVar are set (but are exclusive)"
		exit 1
	fi
	local val="$def"
	if [ "${!var:-}" ]; then
		val="${!var}"
	elif [ "${!fileVar:-}" ]; then
		val="$(< "${!fileVar}")"
	fi
	export "$var"="$val"
	unset "$fileVar"
}


function data_ready() {
file_env 'DATA_NETLOC'
python << END
import sys
import psycopg2
try:
    psycopg2.connect("${DATA_NETLOC}")
except psycopg2.OperationalError:
    sys.exit(-1)
sys.exit(0)
END
}

until cache_ready; do
  >&2 echo "Cache is unavailable - sleeping"
  sleep 1
done

>&2 echo "Cache is up - continuing..."

until broker_ready; do
  >&2 echo "Broker is unavailable (sleeping)..."
  sleep 1
done

>&2 echo "Broker is up - continuing..."

until data_ready; do
  >&2 echo "Data is unavailable (sleeping)..."
  sleep 1
done

>&2 echo "Data is up - continuing..."

exec "$@"
