#!/bin/bash
set -ex
if [ ! -d examples ]; then
  git subtree add  --prefix=examples git@github.com:scalingpythonml/scalingpythonml.git master
fi
git subtree pull  --prefix=examples git@github.com:scalingpythonml/scalingpythonml.git master
if [ ! -d message-backend-ray ]; then
  git subtree add  --prefix=message-backend-ray git@github.com:PigsCanFlyLabs/message-backend-ray.git main
fi
git subtree pull  --prefix=message-backend-ray git@github.com:PigsCanFlyLabs/message-backend-ray.git main
