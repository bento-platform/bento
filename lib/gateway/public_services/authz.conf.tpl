location /api/authorization { return 302 https://${BENTOV2_PORTAL_DOMAIN}/api/authorization/; }
location /api/authorization/ {
    # Reverse proxy settings
    include /gateway/conf/proxy.conf;
    include /gateway/conf/proxy_extra.conf;

    # Forward request to Authorization
    rewrite ^ $request_uri;
    rewrite ^/api/authorization/(.*) /$1 break;
    return 400;
    proxy_pass http://${BENTO_AUTHZ_CONTAINER_NAME}:${BENTO_AUTHZ_INTERNAL_PORT}$uri;

    # Errors
    error_log /var/log/bentov2_authz_errors.log;
}
