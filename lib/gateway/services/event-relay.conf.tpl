location /api/event-relay { return 302 https://${BENTOV2_PORTAL_DOMAIN}/api/event-relay/; }
location /api/event-relay/ {
    # Reverse proxy settings
    include /gateway/conf/proxy.conf;
    include /gateway/conf/proxy_extra.conf;
    include /gateway/conf/proxy_private.conf;

    # Forward request to event-relay
    rewrite ^ $request_uri;
    rewrite ^/api/event-relay/(.*) /$1 break;
    return 400;
    proxy_pass  http://${BENTOV2_EVENT_RELAY_CONTAINER_NAME}:${BENTOV2_EVENT_RELAY_INTERNAL_PORT}$uri;

    # Errors
    error_log /var/log/bentov2_event_relay_errors.log;
}
