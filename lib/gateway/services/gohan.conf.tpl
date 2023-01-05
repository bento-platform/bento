location ~ /api/gohan {
    # Reverse proxy settings
    include /gateway/conf/proxy.conf;
    include /gateway/conf/proxy_extra.conf;
    include /gateway/conf/proxy_private.conf;

    # Remove "/api/gohan" from the path
    rewrite /api/gohan/(.*) /$1  break;

    # Forward request to Gohan
    proxy_pass  http://${BENTOV2_GOHAN_API_CONTAINER_NAME}:${BENTOV2_GOHAN_API_INTERNAL_PORT}/$1$is_args$args;

    # Errors
    error_log /var/log/bentov2_gohan_api_errors.log;
}
