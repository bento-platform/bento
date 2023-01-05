#!/usr/bin/env bash

set -o allexport

source etc/bento.env
if [[ -f "local.env" ]]; then
  source local.env
fi

python3 -m bentoctl.entry "$@"
