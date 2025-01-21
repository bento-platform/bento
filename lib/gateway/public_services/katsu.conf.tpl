location /api/metadata { return 302 https://${BENTOV2_DOMAIN}/api/metadata/; }
location /api/metadata/ {
    # Reverse proxy settings
    include /gateway/conf/proxy.conf;
    include /gateway/conf/proxy_extra.conf;

    # Forward request to Katsu
    rewrite ^ $request_uri;
    rewrite ^/api/metadata/(.*) /$1 break;
    return 400;
    proxy_pass http://${BENTOV2_KATSU_CONTAINER_NAME}:${BENTOV2_KATSU_INTERNAL_PORT}$uri;

    # Errors
    error_log /var/log/bentov2_metadata_errors.log;
}
