location /api/drop-box { return 302 https://${BENTOV2_DOMAIN}/api/drop-box/; }
location /api/drop-box/ {
    # Reverse proxy settings
    include /gateway/conf/proxy.conf;
    include /gateway/conf/proxy_extra.conf;

    # Forward request to the drop box service
    rewrite ^ $request_uri;
    rewrite ^/api/drop-box/(.*) /$1 break;
    return 400;
    proxy_pass http://${BENTOV2_DROP_BOX_CONTAINER_NAME}:${BENTOV2_DROP_BOX_INTERNAL_PORT}$uri;

    # Errors
    error_log /var/log/bentov2_drop_box_errors.log;
}
location /api/drop-box/objects/ {
    # Reverse proxy settings
    include /gateway/conf/proxy.conf;

    # !!! Allow large ingest bodies !!!
    client_body_timeout     660s;
    proxy_read_timeout      660s;
    proxy_send_timeout      660s;
    send_timeout            660s;
    client_max_body_size    0;

    # Forward request to the drop box service
    rewrite ^ $request_uri;
    rewrite ^/api/drop-box/(.*) /$1 break;
    return 400;
    proxy_pass http://${BENTOV2_DROP_BOX_CONTAINER_NAME}:${BENTOV2_DROP_BOX_INTERNAL_PORT}$uri;

    # Errors
    error_log /var/log/bentov2_drop_box_errors.log;
}
