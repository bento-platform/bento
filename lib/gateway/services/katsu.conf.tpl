location ~ /api/metadata {
    # Reverse proxy settings
    include /gateway/conf/proxy.conf;
    include /gateway/conf/proxy_extra.conf;
    include /gateway/conf/proxy_private.conf;

    # Remove "/api/metadata" from the path
    rewrite /api/metadata/(.*) /$1  break;

    # Forward request to Katsu
    proxy_pass    http://${BENTOV2_KATSU_CONTAINER_NAME}:${BENTOV2_KATSU_INTERNAL_PORT}/$1$is_args$args;

    # Errors
    error_log /var/log/bentov2_metadata_errors.log;
}