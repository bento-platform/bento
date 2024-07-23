location /api/metadata { return 302 https://${BENTOV2_PORTAL_DOMAIN}/api/metadata/; }
location /api/metadata/ {
    # Reverse proxy settings
    include /gateway/conf/proxy.conf;
    include /gateway/conf/proxy_extra.conf;
    include /gateway/conf/proxy_private.conf;

    # Forward request to Katsu
    rewrite ^ $request_uri;
    rewrite ^/api/metadata/(.*) /$1 break;
    return 400;
    proxy_pass http://${BENTOV2_KATSU_CONTAINER_NAME}:${BENTOV2_KATSU_INTERNAL_PORT}$uri;

    # CORS
    include /usr/local/openresty/nginx/conf/cors.conf;

    # Errors
    error_log /var/log/bentov2_metadata_errors.log;
}
