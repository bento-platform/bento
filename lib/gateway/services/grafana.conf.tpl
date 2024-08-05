location /api/grafana { return 302 https://${BENTOV2_PORTAL_DOMAIN}/api/grafana/; }
location /api/grafana/ {
    # Reverse proxy settings
    include /gateway/conf/proxy.conf;
    include /gateway/conf/proxy_extra.conf;

    proxy_pass http://bentov2-grafana:3000;
    error_log /var/log/bentov2_grafana_errors.log;
}
