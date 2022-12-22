location ~ /api/event-relay {
    # Reverse proxy settings
    include /gateway/conf/proxy.conf;
    include /gateway/conf/proxy_extra.conf;
    include /gateway/conf/proxy_private.conf;

    # Remove "/api/event-relay" from the path
    rewrite /api/event-relay/(.*) /$1  break;

    # Forward request to event-relay service
    proxy_pass  http://${BENTOV2_EVENT_RELAY_CONTAINER_NAME}:${BENTOV2_EVENT_RELAY_INTERNAL_PORT}/$1$is_args$args;

    # Errors
    error_log /var/log/bentov2_event_relay_errors.log;
}
