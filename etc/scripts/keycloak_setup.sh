#! /usr/bin/env bash
set -e

# checks for dev or prod
if [[ $MODE == "dev" ]]
  then
    DEV_FLAG="-k"
fi
echo "--- MODE : ${MODE} ---"

# This script will set up a full keycloak environment on your local BentoV2 cluster

usage () {
  echo "Make sure to set relevant environment variables!"
  echo "Current setup: "
  echo "BENTOV2_AUTH_ADMIN_USER: ${BENTOV2_AUTH_ADMIN_USER}"
  echo "BENTOV2_AUTH_ADMIN_PASSWORD: ${BENTOV2_AUTH_ADMIN_PASSWORD}"
  echo "BENTOV2_AUTH_TEST_USER: ${BENTOV2_AUTH_TEST_USER}"
  echo "BENTOV2_AUTH_TEST_PASSWORD: ${BENTOV2_AUTH_TEST_PASSWORD}"
  echo "BENTOV2_AUTH_PUBLIC_URL: ${BENTOV2_AUTH_PUBLIC_URL}"
  echo "KEYCLOAK_SERVICE_PUBLIC_PORT: ${KEYCLOAK_SERVICE_PUBLIC_PORT}"
  echo "BENTOV2_AUTH_CONTAINER_NAME: ${BENTOV2_AUTH_CONTAINER_NAME}"

  echo
}


# Load Keycloak template (.tpl) files, populate them 
# with project .env variables, and then spit 
# them out to ./lib/keyclaok/data/*

mkdir -p $BENTOV2_AUTH_VOL_DIR
sudo chown $USER $BENTOV2_AUTH_VOL_DIR

# temp: in prod mode, explicitly indicating port 443 breaks vaults internal oidc provider checks.
# simply remove the ":443 from the authentication services public url for this purpose:
if [[ $BENTOV2_AUTH_PUBLIC_URL == *":443"* ]]; then
    TEMP_BENTOV2_AUTH_PUBLIC_URL=$(echo $BENTOV2_AUTH_PUBLIC_URL | sed -e 's/\(:443\)$//g')
elif [[ $BENTOV2_AUTH_PUBLIC_URL == *":80"* ]]; then
    TEMP_BENTOV2_AUTH_PUBLIC_URL=$(echo $BENTOV2_AUTH_PUBLIC_URL | sed -e 's/\(:80\)$//g')
else
    TEMP_BENTOV2_AUTH_PUBLIC_URL=$(echo $BENTOV2_AUTH_PUBLIC_URL)
fi

export TEMP_BENTOV2_AUTH_PUBLIC_URL


# echo 
mkdir -p $BENTOV2_AUTH_VOL_DIR
chmod 777 $BENTOV2_AUTH_VOL_DIR


# Copy files from template configs
echo "Copying application-users.properties .."
cp ${PWD}/etc/templates/auth/application-users.properties $BENTOV2_AUTH_VOL_DIR/application-users.properties

echo "Copying logging.properties .."
cp ${PWD}/etc/templates/auth/logging.properties $BENTOV2_AUTH_VOL_DIR/logging.properties

echo "Copying mgmt-users.properties .."
cp ${PWD}/etc/templates/auth/mgmt-users.properties $BENTOV2_AUTH_VOL_DIR/mgmt-users.properties

echo "Copying standalone.xml .."
cp ${PWD}/etc/templates/auth/standalone.xml $BENTOV2_AUTH_VOL_DIR/standalone.xml

echo "Copying standalone-ha.xml .."
cp ${PWD}/etc/templates/auth/standalone-ha.xml $BENTOV2_AUTH_VOL_DIR/standalone-ha.xml



# Verify if keycloak container is running
KEYCLOAK_CONTAINERS=$(echo $(docker ps | grep keycloak | wc -l))
echo "Number of keycloak containers running: ${KEYCLOAK_CONTAINERS}"
if [[ $KEYCLOAK_CONTAINERS -eq 0 ]]; then
   echo "Booting keycloak container!"
   docker-compose -f ${PWD}/docker-compose.yaml up -d auth
   sleep 5

   echo ">> .. waiting for keycloak to start..."
   while !  docker logs --tail 1000  ${BENTOV2_AUTH_CONTAINER_NAME} | grep "Undertow HTTPS listener https listening on 0.0.0.0" ; do sleep 1 ; done
   echo ">> .. ready..."
fi


###############

add_users() {
  # BENTOV2_AUTH_CONTAINER_NAME is the name of the keycloak server inside the compose network
  echo "Adding ${BENTOV2_AUTH_TEST_USER}"
  docker exec ${BENTOV2_AUTH_CONTAINER_NAME} \
    /opt/keycloak/bin/kcadm.sh \
    create users \
    -s "username=${BENTOV2_AUTH_TEST_USER}" \
    -s "password=${BENTOV2_AUTH_TEST_PASSWORD}" \
    -s "enabled=true" \
    -r "${BENTOV2_AUTH_REALM}" \
    --no-config \
    --server http://localhost:8080 \
    --user ${BENTOV2_AUTH_TEST_USER} \
    --password ${BENTOV2_AUTH_TEST_PASSWORD} \
    --realm master

  echo "Restarting the keycloak container"
  docker restart ${BENTOV2_AUTH_CONTAINER_NAME}
}

get_user_id () {
  KUID=$(curl \
    -H "Authorization: bearer ${KC_TOKEN}" \
    "${BENTOV2_AUTH_PUBLIC_URL}/admin/realms/${BENTOV2_AUTH_REALM}/users" $DEV_FLAG 2> /dev/null )
  echo ${KUID} | python3 -c 'import json,sys;obj=json.load(sys.stdin);print(obj[0]["id"])'
}

###############

get_token () {
  BID=$(curl \
    -d "client_id=admin-cli" \
    -d "username=$BENTOV2_AUTH_ADMIN_USER" \
    -d "password=$BENTOV2_AUTH_ADMIN_PASSWORD" \
    -d "grant_type=password" \
    "${BENTOV2_AUTH_PUBLIC_URL}/realms/master/protocol/openid-connect/token" $DEV_FLAG 2> /dev/null )
  echo "BID: ${BID}";
  echo ${BID} | python3 -c 'import json,sys;obj=json.load(sys.stdin);print(obj["access_token"])'
}

###############

set_realm () {
  realm=$1

  docker exec "${BENTOV2_AUTH_CONTAINER_NAME}" \
    /opt/keycloak/bin/kcadm.sh \
    create realms \
    -s "realm=${realm}" \
    -s "enabled=true" \
    -r "${BENTOV2_AUTH_REALM}" \
    --no-config \
    --server http://localhost:8080 \
    --user "${BENTOV2_AUTH_ADMIN_USER}" \
    --password "${BENTOV2_AUTH_ADMIN_PASSWORD}" \
    --realm master
#      --password ${BENTOV2_AUTH_TEST_PASSWORD} \
#      --realm master

#  JSON="{\"realm\": \"${realm}\",\"enabled\": true}"
#
#  curl \
#    -H "Authorization: bearer ${KC_TOKEN}" \
#    -X POST -H "Content-Type: application/json"  -d "${JSON}" \
#    "${BENTOV2_AUTH_PUBLIC_URL}/admin/realms" $DEV_FLAG
}


get_realm () {
  realm=$1

  curl \
    -H "Authorization: bearer ${KC_TOKEN}" \
    "${BENTOV2_AUTH_PUBLIC_URL}/admin/realms/${realm}" $DEV_FLAG | jq .
}

#################################

get_realm_clients () {
  realm=$1

  curl \
    -H "Authorization: bearer ${KC_TOKEN}" \
    "${BENTOV2_AUTH_PUBLIC_URL}/admin/realms/${realm}/clients" $DEV_FLAG | jq -S .
}


#################################
set_client () {
  realm=$1
  client=$2
  redirect=$3

  # Will add / to listen only if it is present

  JSON='{
    "clientId": "'"${client}"'",
    "enabled": true,
    "protocol": "openid-connect",
    "implicitFlowEnabled": true,
    "standardFlowEnabled": true,
    "publicClient": false,
    "redirectUris": [
      "'${BENTOV2_PORTAL_PUBLIC_URL}${redirect}'"
    ],
    "attributes": {
      "saml.assertion.signature": "false",
      "saml.authnstatement": "false",
      "saml.client.signature": "false",
      "saml.encrypt": "false",
      "saml.force.post.binding": "false",
      "saml.multivalued.roles": "false",
      "saml.onetimeuse.condition": "false",
      "saml.server.signature": "false",
      "saml.server.signature.keyinfo.ext": "false",
      "saml_force_name_id_format": "false"
    }
  }'
  echo $JSON
  curl \
    -H "Authorization: bearer ${KC_TOKEN}" \
    -X POST -H "Content-Type: application/json"  -d "${JSON}" \
    "${BENTOV2_AUTH_PUBLIC_URL}/admin/realms/${realm}/clients" $DEV_FLAG
}

get_secret () {
  id=$(curl -H "Authorization: bearer ${KC_TOKEN}" \
    ${BENTOV2_AUTH_PUBLIC_URL}/admin/realms/${BENTOV2_AUTH_REALM}/clients $DEV_FLAG 2> /dev/null \
    | python3 -c 'import json,sys;obj=json.load(sys.stdin); print([l["id"] for l in obj if l["clientId"] ==
    "'"$BENTOV2_AUTH_CLIENT_ID"'" ][0])')

  curl -H "Authorization: bearer ${KC_TOKEN}" \
    ${BENTOV2_AUTH_PUBLIC_URL}/admin/realms/${BENTOV2_AUTH_REALM}/clients/$id/client-secret $DEV_FLAG 2> /dev/null |\
    python3 -c 'import json,sys;obj=json.load(sys.stdin); print(obj["value"])'
}

get_public_key () {
  curl \
    ${BENTOV2_AUTH_PUBLIC_URL}/realms/${BENTOV2_AUTH_REALM} $DEV_FLAG 2> /dev/null |\
    python3 -c 'import json,sys;obj=json.load(sys.stdin); print(obj["public_key"])'
}
##################################

# SCRIPT START

echo "-- Starting setup calls to keycloak --"
echo "$BENTOV2_AUTH_ADMIN_USER $BENTOV2_AUTH_ADMIN_PASSWORD $BENTOV2_AUTH_PUBLIC_URL"

echo ">> Getting KC_TOKEN .."
KC_TOKEN=$(get_token)
echo ">> retrieved KC_TOKEN ${KC_TOKEN}"
echo ">> .. got it..."

echo ">> Creating Realm ${BENTOV2_AUTH_REALM} .."
set_realm ${BENTOV2_AUTH_REALM}
echo ">> .. created..."


echo ">> Setting client ${BENTOV2_AUTH_CLIENT_ID} .."
set_client ${BENTOV2_AUTH_REALM} ${BENTOV2_AUTH_CLIENT_ID} "${BENTOV2_AUTH_LOGIN_REDIRECT_PATH}"
echo ">> .. set..."

echo ">> Getting CLIENT_SECRET .."
export CLIENT_SECRET=$(get_secret  ${BENTOV2_AUTH_REALM})
echo "** Retrieved CLIENT_SECRET as ${CLIENT_SECRET} **"
echo ">> .. got it..."
echo


echo ">> Getting KC_PUBLIC_KEY .."
export KC_PUBLIC_KEY=$(get_public_key  ${BENTOV2_AUTH_REALM})
echo "** Retrieved KC_PUBLIC_KEY as ${KC_PUBLIC_KEY} **"
echo ">> .. got it..."
echo


echo ">> Adding user .."
add_users
echo ">> .. added..."
echo 

echo ">> .. waiting for keycloak to restart..."
while !  docker logs --tail 5  ${BENTOV2_AUTH_CONTAINER_NAME} | grep "Admin console listening on http://127.0.0.1:9990" ; do sleep 1 ; done
echo ">> .. ready..."


# echo ">> Getting fresh KC_TOKEN .."
# KC_TOKEN=$(get_token)
# #echo ">> retrieved KC_TOKEN ${KC_TOKEN}"
# echo ">> .. got it..."


# echo ">> Getting user id .."
# export KEYCLOAK_USER_ID=$(get_user_id)
# echo "** Retrieved KEYCLOAK_USER_ID as ${KEYCLOAK_USER_ID} **"
# echo ">> .. got it..."
# echo