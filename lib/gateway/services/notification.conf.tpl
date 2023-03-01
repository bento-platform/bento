location ~ /api/notification {
    # Reverse proxy settings
    include /gateway/conf/proxy.conf;
    include /gateway/conf/proxy_extra.conf;
    include /gateway/conf/proxy_private.conf;

    # Remove "/api/notification" from the path
    rewrite /api/notification/(.*) /$1  break;

    # Forward request to notification service
    proxy_pass  http://${BENTOV2_NOTIFICATION_CONTAINER_NAME}:${BENTOV2_NOTIFICATION_INTERNAL_PORT}/$1$is_args$args;

    # Errors
    error_log /var/log/bentov2_notification_errors.log;
}
