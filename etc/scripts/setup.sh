#! /usr/bin/env bash
set -e

# checks for dev or prod
if [ $MODE == "" ]
  then
    echo "Please check the MODE in your environment varibles!"
    exit 1
fi


# -- Prerequisites --
echo
echo "- Generating prerequisites; -"

export BENTOV2_AUTH_CLIENT_ID_64=$(echo -n ${BENTOV2_AUTH_CLIENT_ID} | base64)
echo "Generated BENTOV2_AUTH_CLIENT_ID_64 as ${BENTOV2_AUTH_CLIENT_ID_64}"

echo "- Done with prereqs.. -"
# --

echo
echo "Setting up Keycloak;"
bash ${PWD}/etc/scripts/keycloak_setup.sh 

echo
echo "-- Auth Setup Done! --"
echo
