location ~ /api/reference {
    # Reverse proxy settings
    include /gateway/conf/proxy.conf;
    include /gateway/conf/proxy_extra.conf;
    include /gateway/conf/proxy_private.conf;

    # Remove "/api/reference" from the path
    rewrite /api/reference/(.*) /$1  break;

    # Forward request to the Bento Reference Service
    proxy_pass  http://${BENTO_REFERENCE_CONTAINER_NAME}:${BENTO_REFERENCE_INTERNAL_PORT}/$1$is_args$args;

    # Errors
    error_log /var/log/bentov2_reference_errors.log;
}
