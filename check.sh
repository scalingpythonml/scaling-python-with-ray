#!/bin/bash
set -ex

# Configure us to use the integrated settings
export DJANGO_SETTINGS_MODULE="messaging.web.src.config.settings"
export DJANGO_CONFIGURATION="unit_test"

nosetests -vs --traverse-namespace messaging
flake8 messaging --max-line-length=100  --exclude "*/proto/* */web/*"
mypy messaging --exclude "/proto/" --exclude "/web/"
