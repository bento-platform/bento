location /api/reference { return 302 https://${BENTOV2_DOMAIN}/api/reference/; }
location /api/reference/ {
    # Reverse proxy settings
    include /gateway/conf/proxy.conf;
    include /gateway/conf/proxy_extra.conf;

    # Forward request to reference service
    rewrite ^ $request_uri;
    rewrite ^/api/reference/(.*) /$1 break;
    return 400;
    proxy_pass  http://${BENTO_REFERENCE_CONTAINER_NAME}:${BENTO_REFERENCE_INTERNAL_PORT}$uri;

    # Errors
    error_log /var/log/bento_reference_errors.log;
}
