location ~ /api/aggregation {
    # Reverse proxy settings
    include /gateway/conf/proxy.conf;
    include /gateway/conf/proxy_extra.conf;
    include /gateway/conf/proxy_private.conf;

    # Remove "/api/aggregation" from the path
    rewrite /api/aggregation/(.*) /$1  break;

    # Forward request to the aggregation
    proxy_pass  http://${BENTOV2_AGGREGATION_CONTAINER_NAME}:${BENTOV2_AGGREGATION_INTERNAL_PORT}/$1$is_args$args;

    # Errors
    error_log /var/log/bentov2_aggregation_errors.log;
}
