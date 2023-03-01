location ~ /api/wes {
    # Reverse proxy settings
    include /gateway/conf/proxy.conf;
    include /gateway/conf/proxy_extra.conf;
    include /gateway/conf/proxy_private.conf;

    # Remove "/api/wes" from the path
    rewrite /api/wes/(.*) /$1  break;

    # Forward request to WES
    proxy_pass  http://${BENTOV2_WES_CONTAINER_NAME}:${BENTOV2_WES_INTERNAL_PORT}/$1$is_args$args;

    # Errors
    error_log /var/log/bentov2_wes_errors.log;
}
