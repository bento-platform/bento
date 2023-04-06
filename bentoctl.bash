#!/usr/bin/env bash

set -o allexport

# Sourcing order
#  1. default_config.env (declare some defaults for configurable variables / make them exist)
#  2. local.env          (overrides for default config)
#  3. bento.env          (uses some local.env values)
#  4. local.env *again*  (overrides for bento.env values, e.g. versions)

source etc/default_config.env
if [[ -f "local.env" ]]; then
  source local.env
fi
source etc/bento.env
if [[ -f "local.env" ]]; then
  source local.env
fi

python3 -m py_bentoctl.entry "$@"
