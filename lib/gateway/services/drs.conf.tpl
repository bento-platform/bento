location /api/drs { return 302 https://${BENTOV2_PORTAL_DOMAIN}/api/drs/; }
location /api/drs/ {
    # Reverse proxy settings
    include /gateway/conf/proxy.conf;
    include /gateway/conf/proxy_extra.conf;
    include /gateway/conf/proxy_private.conf;

    # Forward request to DRS
    rewrite ^ $request_uri;
    rewrite ^/api/drs/(.*) /$1 break;
    return 400;
    proxy_pass http://${BENTOV2_DRS_CONTAINER_NAME}:${BENTOV2_DRS_INTERNAL_PORT}$uri;

    # Errors
    error_log /var/log/bentov2_drs_errors.log;
}
