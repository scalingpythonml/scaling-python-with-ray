#!/bin/bash
# On codespaces we can't yet change the workdir in the config so change it in our entrypoint.
if [ ! -z "${CODESPACE_VSCODE_FOLDER}" ]; then
  cd ${CODESPACE_VSCODE_FOLDER}
fi
start-notebook.sh
