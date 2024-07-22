location /api/grafana { return 302 https://${BENTOV2_PORTAL_DOMAIN}/api/grafana/; }
location /api/grafana/ {
    # Reverse proxy settings
    include /gateway/conf/proxy.conf;
    include /gateway/conf/proxy_extra.conf;

    set $auth $http_Authorization;
    proxy_pass_request_headers on;
    if ($cookie_jwt) {
        set $auth $cookie_jwt;
    }
    proxy_set_header Authorization $auth;

    proxy_pass http://bentov2-grafana:3000;
    if ($http_Authorization) {
        add_header Set-Cookie 'jwt=$http_Authorization; Path=/api/grafana; HttpOnly; Secure' always;
    }

    error_log /var/log/bentov2_grafana_errors.log;
}
