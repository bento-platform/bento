location /api/service-registry { return 302 https://${BENTOV2_PORTAL_DOMAIN}/api/service-registry/; }
location /api/service-registry/ {
    # Reverse proxy settings
    include /gateway/conf/proxy.conf;
    include /gateway/conf/proxy_extra.conf;
    include /gateway/conf/proxy_private.conf;

    # Forward request to the service-registry
    rewrite ^ $request_uri;
    rewrite ^/api/service-registry/(.*) /$1 break;
    return 400;
    proxy_pass http://${BENTOV2_SERVICE_REGISTRY_CONTAINER_NAME}:${BENTOV2_SERVICE_REGISTRY_INTERNAL_PORT}$uri;

    # Errors
    error_log /var/log/bentov2_service_registry_errors.log;
}
