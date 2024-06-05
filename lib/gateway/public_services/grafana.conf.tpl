location /api/grafana { return 302 https://${BENTOV2_DOMAIN}/api/grafana/; }
location /api/grafana/ {
    # Reverse proxy settings
    include /gateway/conf/proxy.conf;

    add_header Content-Security-Policy "frame-ancestors 'self' https://${BENTOV2_DOMAIN};";
    # Immediate set/re-use means we don't get resolve errors if not up (as opposed to passing as a literal)
    set $upstream_cbio http://bentov2-grafana:3000;

    proxy_pass $upstream_cbio;
    error_log /var/log/bentov2_grafana_errors.log;
}
