#!/bin/bash
brew install bazelisk wget python@3.8 npm
# Make sure homebrew Python is used before system Python
export PATH=$(brew --prefix)/opt/python@3.8/bin/:$PATH
echo "export PATH=$(brew --prefix)/opt/python@3.8/bin/:$PATH" >> ~/.zshrc
echo "export PATH=$(brew --prefix)/opt/python@3.8/bin/:$PATH" >> ~/.bashrc
# Install some libraries vendored incorrectly by Ray for ARM
pip3 install --user psutil cython colorama
