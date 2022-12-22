location ~ /api/drs {
    # Reverse proxy settings
    include /gateway/conf/proxy.conf;
    include /gateway/conf/proxy_extra.conf;
    include /gateway/conf/proxy_private.conf;

    # Remove "/api/drop-box" from the path
    rewrite /api/drs/(.*) /$1  break;

    # Forward request to the drop-box
    proxy_pass  http://${BENTOV2_DRS_CONTAINER_NAME}:${BENTOV2_DRS_INTERNAL_PORT}/$1$is_args$args;

    # Errors
    error_log /var/log/bentov2_drs_errors.log;
}
