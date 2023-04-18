location /api/aggregation/ {
    # Reverse proxy settings
    include /gateway/conf/proxy.conf;
    include /gateway/conf/proxy_extra.conf;
    include /gateway/conf/proxy_private.conf;

    # Forward request to the aggregation
    proxy_pass  http://${BENTOV2_AGGREGATION_CONTAINER_NAME}:${BENTOV2_AGGREGATION_INTERNAL_PORT}/;

    # Errors
    error_log /var/log/bentov2_aggregation_errors.log;
}
