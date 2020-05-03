#!/bin/bash
pushd /falco
./build/init.sh
make -j 4
popd
