# env: BENTO_GOHAN_ENABLED
location /api/gohan { return 302 https://${BENTOV2_PORTAL_DOMAIN}/api/gohan/; }
location /api/gohan/ {
    # Reverse proxy settings
    include /gateway/conf/proxy.conf;
    include /gateway/conf/proxy_extra.conf;
    include /gateway/conf/proxy_private.conf;

    # Forward request to Gohan
    rewrite ^ $request_uri;
    rewrite ^/api/gohan/(.*) /$1 break;
    return 400;
    proxy_pass http://${BENTOV2_GOHAN_API_CONTAINER_NAME}:${BENTOV2_GOHAN_API_INTERNAL_PORT}$uri;

    # Errors
    error_log /var/log/bentov2_gohan_api_errors.log;
}
