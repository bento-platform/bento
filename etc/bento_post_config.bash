#!/usr/bin/env bash

if [[ "$BENTO_GATEWAY_USE_TLS" == 'true' || "$BENTO_GATEWAY_USE_TLS" == '1' ]]; then
  KC_HOSTNAME=${BENTOV2_AUTH_DOMAIN}
  KC_HTTP_ENABLED='false'
  KC_HTTPS_CERTIFICATE_FILE=/run/secrets/keycloak-cert-file
  KC_HTTPS_CERTIFICATE_KEY_FILE=/run/secrets/keycloak-cert-key-file
  KC_PROXY='passthrough'
else
  # Disable TLS in keycloak
  KC_HOSTNAME=https://${BENTOV2_AUTH_DOMAIN}  # full URL with HTTPS when KC_HTTP_ENABLED=true
  KC_HTTP_ENABLED='true'      # Required for TLS termination at the proxy
  KC_PROXY='edge'
  KC_PROXY_HEADERS=xforwarded # xforwarded (non-standard) instead of forwarded (RFC7239) for NGINX compatibility
fi
