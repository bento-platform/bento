location /api/event-relay/ {
    # Reverse proxy settings
    include /gateway/conf/proxy.conf;
    include /gateway/conf/proxy_extra.conf;
    include /gateway/conf/proxy_private.conf;

    # Forward request to event-relay
    proxy_pass  http://${BENTOV2_EVENT_RELAY_CONTAINER_NAME}:${BENTOV2_EVENT_RELAY_INTERNAL_PORT}/;

    # Errors
    error_log /var/log/bentov2_event_relay_errors.log;
}
