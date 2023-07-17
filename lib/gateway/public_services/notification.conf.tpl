location /api/notification { return 302 https://${BENTOV2_DOMAIN}/api/notification/; }
location /api/notification/ {
    # Reverse proxy settings
    include /gateway/conf/proxy.conf;
    include /gateway/conf/proxy_extra.conf;

    # Forward request to notification service
    rewrite ^ $request_uri;
    rewrite ^/api/notification/(.*) /$1 break;
    return 400;
    proxy_pass  http://${BENTOV2_NOTIFICATION_CONTAINER_NAME}:${BENTOV2_NOTIFICATION_INTERNAL_PORT}$uri;

    # Errors
    error_log /var/log/bentov2_notification_errors.log;
}
