#! /usr/bin/env bash
set -e


# -- Prerequisites --
echo
echo "- Generating prerequisites; -"

export BENTOV2_AUTH_CLIENT_ID_64=$(echo -n ${BENTOV2_AUTH_CLIENT_ID} | base64)
echo "Generated BENTOV2_AUTH_CLIENT_ID_64 as ${BENTOV2_AUTH_CLIENT_ID_64}"

echo "- Done with prereqs.. -"
# --

if [ $BENTOV2_USE_EXTERNAL_IDP == 1 ]
then
    echo "Using External IDP --";
    echo "Nothing to see here..";
else
    echo "Using Internal IDP --";
    echo "Setting up Keycloak;";
    source ${PWD}/etc/scripts/keycloak_setup.sh ;
fi

# echo "Exporting auth_config to gateway"
# envsubst < ${PWD}/etc/templates/auth_config.example.json > ${PWD}/lib/gateway/auth_config.json;


echo
echo "-- Auth Setup Done! --"
echo
