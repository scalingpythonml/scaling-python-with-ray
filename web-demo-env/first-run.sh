#!/bin/bash
# On codespaces using jupyter as the entrypoint doesn't work so great
# 
set -x
if [ ! -f /tmp/running ] || [ $(kill -s 0 $(cat /tmp/running)) ]; then
  start-notebook.sh --NotebookApp.allow_origin='*' &
  echo $! > /tmp/running
  jupyter notebook list
fi
