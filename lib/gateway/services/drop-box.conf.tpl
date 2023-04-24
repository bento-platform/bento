location /api/drop-box { return 302 https://${BENTOV2_PORTAL_DOMAIN}/api/drop-box/; }
location /api/drop-box/ {
    # Reverse proxy settings
    include /gateway/conf/proxy.conf;
    include /gateway/conf/proxy_extra.conf;
    include /gateway/conf/proxy_private.conf;

    # Forward request to the drop-box
    rewrite ^ $request_uri;
    rewrite ^/api/drop-box/(.*) /$1 break;
    return 400;
    proxy_pass http://${BENTOV2_DROP_BOX_CONTAINER_NAME}:${BENTOV2_DROP_BOX_INTERNAL_PORT}$uri;

    # Errors
    error_log /var/log/bentov2_drop_box_errors.log;
}
