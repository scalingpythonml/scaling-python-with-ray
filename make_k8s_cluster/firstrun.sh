#!/bin/bash
set -ex
# Installing falco
pushd /falco
./init.sh
make -j 4
popd
