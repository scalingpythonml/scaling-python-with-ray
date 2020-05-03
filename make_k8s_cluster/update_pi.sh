#!/bin/bash
DEBIAN_FRONTEND=noninteractive
export DEBIAN_FRONTEND
apt-get update
apt-get upgrade -y
# Set up falco
apt-get install -y tmate

