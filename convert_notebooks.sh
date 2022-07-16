#!/bin/bash
set -ex
find . -name "*ipynb" |grep -v venv |grep -v .ipynb_checkpoints | xargs -d '\n' jupyter nbconvert --to script
