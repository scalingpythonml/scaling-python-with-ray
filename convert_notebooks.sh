#!/bin/bash
find . -name "*ipynb" |grep -v venv |grep -v .ipynb_checkpoints | xargs -d '\n' ipython3 nbconvert --to script
