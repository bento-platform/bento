location /api/wes { return 302 https://${BENTOV2_DOMAIN}/api/wes/; }
location /api/wes/ {
    # Reverse proxy settings
    include /gateway/conf/proxy.conf;
    include /gateway/conf/proxy_extra.conf;

    # Forward request to WES
    rewrite ^ $request_uri;
    rewrite ^/api/wes/(.*) /$1 break;
    return 400;
    proxy_pass  http://${BENTOV2_WES_CONTAINER_NAME}:${BENTOV2_WES_INTERNAL_PORT}$uri;

    # Errors
    error_log /var/log/bentov2_wes_errors.log;
}
