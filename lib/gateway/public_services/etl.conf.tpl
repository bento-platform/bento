location /api/etl { return 302 https://${BENTOV2_DOMAIN}/api/etl/; }
location /api/etl/ {
    # Reverse proxy settings
    include /gateway/conf/proxy.conf;
    include /gateway/conf/proxy_extra.conf;

    # Forward request to ETL
    rewrite ^ $request_uri;
    rewrite ^/api/etl/(.*) /$1 break;
    return 400;
    proxy_pass http://${BENTO_ETL_CONTAINER_NAME}:${BENTO_ETL_INTERNAL_PORT}$uri;

    # Errors
    error_log /var/log/bento_etl_errors.log;
}