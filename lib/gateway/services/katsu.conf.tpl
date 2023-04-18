location /api/metadata/ {
    # Reverse proxy settings
    include /gateway/conf/proxy.conf;
    include /gateway/conf/proxy_extra.conf;
    include /gateway/conf/proxy_private.conf;

    # Forward request to Katsu
    proxy_pass    http://${BENTOV2_KATSU_CONTAINER_NAME}:${BENTOV2_KATSU_INTERNAL_PORT}/;

    # Errors
    error_log /var/log/bentov2_metadata_errors.log;
}