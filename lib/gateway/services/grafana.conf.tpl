# env: BENTO_MONITORING_ENABLED
location /api/grafana { return 302 https://${BENTOV2_PORTAL_DOMAIN}/api/grafana/; }
location /api/grafana/ {
    # Reverse proxy settings
    include /gateway/conf/proxy.conf;
    include /gateway/conf/proxy_extra.conf;
    
    # Immediate set/re-use means we don't get resolve errors if not up (as opposed to passing as a literal)
    set $upstream_grafana http://${BENTO_GRAFANA_CONTAINER_NAME}:3000;
    
    proxy_pass $upstream_grafana;
    error_log /var/log/bentov2_grafana_errors.log;
}
