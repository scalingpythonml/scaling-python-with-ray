#!/bin/bash
# On codespaces using jupyter as the entrypoint doesn't work so great
# 
if [ ! -f /tmp/running ] || [ $(kill -s 0 $(cat /tmp/running)) ]; then
  start-notebook.sh &
  echo $! > /tmp/running
fi
