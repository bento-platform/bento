#!/usr/bin/env bash

set -o allexport

source etc/default_config.env
if [[ -f "local.env" ]]; then
  source local.env
fi
source etc/bento.env

echo "$BENTOV2_WES_VOL_TMP_DIR"

python3 -m py_bentoctl.entry "$@"
