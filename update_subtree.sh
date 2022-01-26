#!/bin/bash
set -ex
if [ ! -d examples ]; then
  git subtree add  --prefix=examples git@github.com:scalingpythonml/scalingpythonml.git master
fi
git subtree pull  --prefix=examples git@github.com:scalingpythonml/scalingpythonml.git master
