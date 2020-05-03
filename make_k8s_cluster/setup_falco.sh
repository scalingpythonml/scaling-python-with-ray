#!/bin/bash
pushd /falco
pushd build
./init.sh
make -j 4
popd
popd
