#!/bin/bash
set -ex

nosetests -vs --traverse-namespace messaging
flake8 messaging --max-line-length=100  --exclude "*/proto/*"
mypy messaging --exclude "/proto/"
