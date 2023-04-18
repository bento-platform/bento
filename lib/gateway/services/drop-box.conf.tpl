location /api/drop-box/ {
    # Reverse proxy settings
    include /gateway/conf/proxy.conf;
    include /gateway/conf/proxy_extra.conf;
    include /gateway/conf/proxy_private.conf;

    # Forward request to the drop-box
    proxy_pass  http://${BENTOV2_DROP_BOX_CONTAINER_NAME}:${BENTOV2_DROP_BOX_INTERNAL_PORT}/;

    # Errors
    error_log /var/log/bentov2_drop_box_errors.log;
}
