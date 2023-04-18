location /api/wes/ {
    # Reverse proxy settings
    include /gateway/conf/proxy.conf;
    include /gateway/conf/proxy_extra.conf;
    include /gateway/conf/proxy_private.conf;

    # Forward request to WES
    proxy_pass  http://${BENTOV2_WES_CONTAINER_NAME}:${BENTOV2_WES_INTERNAL_PORT}/;

    # Errors
    error_log /var/log/bentov2_wes_errors.log;
}
