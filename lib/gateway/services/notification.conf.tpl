location /api/notification/ {
    # Reverse proxy settings
    include /gateway/conf/proxy.conf;
    include /gateway/conf/proxy_extra.conf;
    include /gateway/conf/proxy_private.conf;

    # Forward request to notification service
    proxy_pass  http://${BENTOV2_NOTIFICATION_CONTAINER_NAME}:${BENTOV2_NOTIFICATION_INTERNAL_PORT}/;

    # Errors
    error_log /var/log/bentov2_notification_errors.log;
}
