# env: BENTO_BEACON_ENABLED
location /api/beacon { return 302 https://${BENTOV2_DOMAIN}/api/beacon/; }
location /api/beacon/ {
    # Reverse proxy settings
    include /gateway/conf/rate_limit_beacon.conf;  # More aggressive than the proxy.conf ones
    include /gateway/conf/proxy.conf;
    include /gateway/conf/proxy_extra.conf;

    # Forward request to Beacon
    rewrite ^ $request_uri;
    rewrite ^/api/beacon/(.*) /$1 break;
    return 400;
    proxy_pass http://${BENTO_BEACON_CONTAINER_NAME}:${BENTO_BEACON_INTERNAL_PORT}$uri;

    # Errors
    error_log /var/log/bentov2_beacon_errors.log;
}
