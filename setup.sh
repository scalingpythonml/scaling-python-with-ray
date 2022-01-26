#!/bin/bash
# We use asciidoctor-pdf
set -ex

if ! command -v asciidoctor-pdf &> /dev/null; then
  sudo gem install rghost asciidoctor-pdf
fi

# subtree for keeping examples in line
if [ ! -f "$(git --exec-path)"/git-subtree ]; then
  mytmpdir=$(mktemp -d 2>/dev/null || mktemp -d -t 'mytmpdir')
  pushd "${mytmpdir}"
  git clone https://github.com/apenwarr/git-subtree
  pushd git-subtree
  chmod a+x install.sh
  sudo ./install.sh
  popd
  popd
fi
