#!/bin/bash
set -ex
for file in $(find . -name "*ipynb" |grep -v venv |grep -v .ipynb_checkpoints); do
  jupyter nbconvert --to script $file || echo "Bad code?"
done
