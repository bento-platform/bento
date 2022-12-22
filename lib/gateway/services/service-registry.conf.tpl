location ~ /api/service-registry { # ^~ /api/service-registry/
    # Reverse proxy settings
    include /gateway/conf/proxy.conf;
    include /gateway/conf/proxy_extra.conf;
    include /gateway/conf/proxy_private.conf;

    # Remove "/api/service-registry" from the path
    rewrite /api/service-registry/(.*) /$1  break;

    # Forward request to the service-registry
    proxy_pass  http://${BENTOV2_SERVICE_REGISTRY_CONTAINER_NAME}:${BENTOV2_SERVICE_REGISTRY_INTERNAL_PORT}/$1$is_args$args;

    # Errors
    error_log /var/log/bentov2_service_registry_errors.log;
}
