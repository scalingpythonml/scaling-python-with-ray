#!/bin/bash
pushd /falco
pushd build
./init.sh || echo "Failed to setup falco build"
make -j 4 driver || echo "Failed to make falco kernel driver"
popd
popd
