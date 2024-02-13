#!/usr/bin/env bash

# This file is a shim between the user and the `py_bentoctl` management CLI module. Its job is two-fold:
#  - Load any environment variables from the various .env and .bash files, which configure a given Bento deployment.
#  - Pass the configured environment, and CLI arguments, to the Python module.

# Automatically export any variables set in this shell to processes launched from this shell (i.e., `py_bentoctl`):
set -o allexport

# ENVIRONMENT CONFIGURATION --------------------------------------------------------------------------------------------
# Sourcing order:
#  1. default_config.env     (declare some defaults for configurable variables / make them exist)
source etc/default_config.env
#  2. local.env              (overrides for default config)
if [[ -f "local.env" ]]; then source local.env; fi
#  3. bento.env              (uses some local.env values)
source etc/bento.env
#  4. local.env *again*      (overrides for bento.env values, e.g. versions)
if [[ -f "local.env" ]]; then source local.env; fi
#  5. bento_post_config.bash (script, rather than .env, for branching decisions based on environment)
source etc/bento_post_config.bash
# ----------------------------------------------------------------------------------------------------------------------

# After configuring the environment, take any CLI arguments that were passed to this script and forward them to the
# Python bentoctl module, which will perform the actual execution:
python3 -m py_bentoctl.entry "$@"

# Reverse change to variable-setting behaviour from the beginning of the script:
set +o allexport
