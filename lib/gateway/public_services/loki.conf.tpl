location /api/loki { return 302 https://${BENTOV2_DOMAIN}/api/loki/; }
location /api/loki/ {
    # Reverse proxy settings
    include /gateway/conf/proxy.conf;
    include /gateway/conf/proxy_extra.conf;

    # Forward request to the aggregation
    rewrite ^ $request_uri;
    rewrite ^/api/loki/(.*) /$1 break;
    return 400;
    proxy_pass http://bentov2-loki:3100/loki/api/v1$uri;

    # Errors
    error_log /var/log/bentov2_loki_errors.log;
}
