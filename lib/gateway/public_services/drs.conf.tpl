location /api/drs { return 302 https://${BENTOV2_DOMAIN}/api/drs/; }
location /api/drs/ {
    # Reverse proxy settings
    include /gateway/conf/proxy.conf;
    include /gateway/conf/proxy_extra.conf;

    # Forward request to DRS
    rewrite ^ $request_uri;
    rewrite ^/api/drs/(.*) /$1 break;
    return 400;
    proxy_pass http://${BENTOV2_DRS_CONTAINER_NAME}:${BENTOV2_DRS_INTERNAL_PORT}$uri;

    # Errors
    error_log /var/log/bentov2_drs_errors.log;
}
location /ga4gh/drs/v1/objects/ {
    # Special: GA4GH DRS URIs cannot translate into URLs with sub-paths, so DRS needs to handle these URLs without the
    # /api/drs prefix.

    # Reverse proxy settings
    include /gateway/conf/proxy.conf;
    include /gateway/conf/proxy_extra.conf;

    # Forward request to DRS
    rewrite ^ $request_uri;
    rewrite ^/(.*) /$1 break;
    return 400;
    proxy_pass http://${BENTOV2_DRS_CONTAINER_NAME}:${BENTOV2_DRS_INTERNAL_PORT}$uri;

    # Errors
    error_log /var/log/bentov2_drs_errors.log;
}
location /api/drs/ingest {
    # Reverse proxy settings
    include /gateway/conf/proxy.conf;

    # !!! Allow large ingest bodies !!!
    client_body_timeout     660s;
    proxy_read_timeout      660s;
    proxy_send_timeout      660s;
    send_timeout            660s;
    client_max_body_size    0;

    # Forward request to DRS
    rewrite ^ $request_uri;
    rewrite ^/api/drs/(.*) /$1 break;
    return 400;
    proxy_pass http://${BENTOV2_DRS_CONTAINER_NAME}:${BENTOV2_DRS_INTERNAL_PORT}$uri;

    # Errors
    error_log /var/log/bentov2_drs_errors.log;
}
