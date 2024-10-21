location /api/tds { return 302 https://${BENTOV2_PORTAL_DOMAIN}/api/tds/; }
location /api/tds/ {
    # Reverse proxy settings
    include /gateway/conf/proxy.conf;
    include /gateway/conf/proxy_extra.conf;

    # Forward request to TDS
    rewrite ^ $request_uri;
    rewrite ^/api/tds/(.*) /$1 break;
    return 400;
    proxy_pass  http://${BENTO_TDS_CONTAINER_NAME}:${BENTO_TDS_INTERNAL_PORT}$uri;

    # Errors
    error_log /var/log/bento_tds_errors.log;
}
