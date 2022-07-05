#!/bin/bash
set -ex

nosetests -vs .
flake8 . --max-line-length=100  --exclude "*/proto/*"
mypy . --exclude "/proto/"
