#!/bin/bash
set -ex

nosetests -vs --traverse-namespace .
flake8 . --max-line-length=100  --exclude "*/proto/*"
mypy . --exclude "/proto/"
