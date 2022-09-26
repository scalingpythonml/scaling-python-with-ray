#!/bin/bash
set -ex
# Needed for files with spaces.
OIFS="$IFS"
IFS=$'\n'
for file in $(find . -name "*ipynb" |grep -v venv |grep -v .ipynb_checkpoints); do
  jupyter nbconvert --to script $file || echo "Bad code?"
done
IFS="$OIFS"
