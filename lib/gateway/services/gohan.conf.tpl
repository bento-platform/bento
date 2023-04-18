# env: BENTO_GOHAN_ENABLED
location /api/gohan/ {
    # Reverse proxy settings
    include /gateway/conf/proxy.conf;
    include /gateway/conf/proxy_extra.conf;
    include /gateway/conf/proxy_private.conf;

    # Forward request to Gohan
    proxy_pass  http://${BENTOV2_GOHAN_API_CONTAINER_NAME}:${BENTOV2_GOHAN_API_INTERNAL_PORT}/;

    # Errors
    error_log /var/log/bentov2_gohan_api_errors.log;
}
