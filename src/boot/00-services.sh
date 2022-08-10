#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

export

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

function broker_ready(){
  file_env 'BROKER_NETLOC'
  echo "Checking $BROKER_NETLOC"
python << END
import os
import sys
import socket
import kombu
try:
    connection = kombu.Connection("${BROKER_NETLOC}")
    connection.connect()
    connection.release()
except socket.error as e:
    print(e)
    sys.exit(-1)
sys.exit(0)
END
}


function data_ready() {
  file_env 'DATA_NETLOC'
  echo "Checking $DATA_NETLOC"
python << END
import sys
import psycopg2
try:
    psycopg2.connect("${DATA_NETLOC}")
except psycopg2.OperationalError as e:
    print(e)
    sys.exit(-1)
sys.exit(0)
END
}

until broker_ready; do
  >&2 echo "Celery broker is unavailable (sleeping)..."
  sleep 1
done

>&2 echo "Broker is up - continuing..."


until data_ready; do
  >&2 echo "Data is unavailable (sleeping)..."
  sleep 1
done

>&2 echo "Data is up - continuing..."

exec "$@"
