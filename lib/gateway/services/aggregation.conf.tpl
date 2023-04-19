location /api/aggregation { return 302 https://${BENTOV2_PORTAL_DOMAIN}/api/aggregation/; }
location /api/aggregation/ {
    # Reverse proxy settings
    include /gateway/conf/proxy.conf;
    include /gateway/conf/proxy_extra.conf;
    include /gateway/conf/proxy_private.conf;

    # Forward request to the aggregation
    rewrite ^ $request_uri;
    rewrite ^/api/aggregation/(.*) /$1 break;
    return 400;
    proxy_pass http://${BENTOV2_AGGREGATION_CONTAINER_NAME}:${BENTOV2_AGGREGATION_INTERNAL_PORT}$uri;

    # Errors
    error_log /var/log/bentov2_aggregation_errors.log;
}
